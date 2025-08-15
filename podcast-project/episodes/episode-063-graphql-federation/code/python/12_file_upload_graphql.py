#!/usr/bin/env python3
"""
12_file_upload_graphql.py
GraphQL File Upload implementation with Indian e-commerce context
Image uploads, document processing, और bulk data imports के लिए
"""

import os
import uuid
import mimetypes
import hashlib
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

import graphene
from graphene import ObjectType, String, Int, Float, Boolean, List as GrapheneList, Field, Schema, Mutation
from graphene_file_upload.scalars import Upload
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from starlette.graphql import GraphQLApp
import aiofiles
import pillow_heif  # For HEIC image support (iPhone images)
from PIL import Image, ImageOps
import pandas as pd
import json

# Configuration
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_IMAGE_TYPES = {
    'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
    'image/webp', 'image/heic', 'image/heif'  # iPhone formats
}
ALLOWED_DOCUMENT_TYPES = {
    'application/pdf', 'text/csv', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

# Create upload directories
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "products").mkdir(exist_ok=True)
(UPLOAD_DIR / "sellers").mkdir(exist_ok=True)
(UPLOAD_DIR / "documents").mkdir(exist_ok=True)
(UPLOAD_DIR / "bulk").mkdir(exist_ok=True)
(UPLOAD_DIR / "thumbnails").mkdir(exist_ok=True)

# Data Models
@dataclass
class UploadedFile:
    id: str
    filename: str
    original_name: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    uploaded_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ProductImage:
    id: str
    product_id: str
    file_id: str
    alt_text: str
    is_primary: bool
    display_order: int
    url: str
    thumbnail_url: str

@dataclass
class SellerDocument:
    id: str
    seller_id: str
    document_type: str
    file_id: str
    status: str  # pending, verified, rejected
    uploaded_at: datetime
    verified_at: Optional[datetime] = None

@dataclass
class BulkImportJob:
    id: str
    file_id: str
    job_type: str  # products, inventory, pricing
    status: str  # processing, completed, failed
    total_records: int
    processed_records: int
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime] = None

# File Storage Service
class FileStorageService:
    def __init__(self):
        self.uploaded_files: Dict[str, UploadedFile] = {}
        self.product_images: Dict[str, ProductImage] = {}
        self.seller_documents: Dict[str, SellerDocument] = {}
        self.bulk_import_jobs: Dict[str, BulkImportJob] = {}
    
    async def save_file(
        self, 
        upload_file: UploadFile, 
        category: str = "general",
        uploaded_by: Optional[str] = None
    ) -> UploadedFile:
        """File को save करता है और metadata return करता है"""
        
        print(f"📁 Saving file: {upload_file.filename} (category: {category})")
        
        # File validation
        if upload_file.size > MAX_FILE_SIZE:
            raise HTTPException(400, f"File too large: {upload_file.size} bytes. Max: {MAX_FILE_SIZE}")
        
        if upload_file.content_type not in (ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES):
            raise HTTPException(400, f"Unsupported file type: {upload_file.content_type}")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(upload_file.filename).suffix
        safe_filename = f"{file_id}{file_extension}"
        
        # Determine storage directory
        storage_dir = UPLOAD_DIR / category
        storage_dir.mkdir(exist_ok=True)
        file_path = storage_dir / safe_filename
        
        # Save file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await upload_file.read()
                await f.write(content)
            
            print(f"✅ File saved: {file_path}")
            
            # Create file record
            uploaded_file = UploadedFile(
                id=file_id,
                filename=safe_filename,
                original_name=upload_file.filename,
                file_path=str(file_path),
                file_size=len(content),
                mime_type=upload_file.content_type,
                uploaded_at=datetime.now(),
                uploaded_by=uploaded_by
            )
            
            # Process based on file type
            if upload_file.content_type in ALLOWED_IMAGE_TYPES:
                uploaded_file.metadata = await self._process_image(file_path, uploaded_file)
            elif upload_file.content_type in ALLOWED_DOCUMENT_TYPES:
                uploaded_file.metadata = await self._process_document(file_path, uploaded_file)
            
            self.uploaded_files[file_id] = uploaded_file
            return uploaded_file
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            # Cleanup partial file
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(500, f"Failed to save file: {str(e)}")
    
    async def _process_image(self, file_path: Path, uploaded_file: UploadedFile) -> Dict[str, Any]:
        """Image processing - thumbnails, EXIF data, etc."""
        print(f"🖼️ Processing image: {file_path}")
        
        try:
            # Handle HEIC images from iPhone
            if uploaded_file.mime_type in ['image/heic', 'image/heif']:
                pillow_heif.register_heif_opener()
            
            with Image.open(file_path) as img:
                # Get image info
                width, height = img.size
                format_info = img.format
                
                # Fix orientation from EXIF
                img = ImageOps.exif_transpose(img)
                
                # Generate thumbnail
                thumbnail_size = (300, 300)
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumbnail_path = UPLOAD_DIR / "thumbnails" / f"thumb_{uploaded_file.filename}"
                img.save(thumbnail_path, format='JPEG', quality=85)
                
                metadata = {
                    'width': width,
                    'height': height,
                    'format': format_info,
                    'thumbnail_path': str(thumbnail_path),
                    'aspect_ratio': round(width / height, 2),
                    'processed_at': datetime.now().isoformat()
                }
                
                # Extract EXIF data (camera info for product photos)
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    if exif_data:
                        # Common EXIF tags
                        camera_info = {}
                        if 271 in exif_data:  # Make
                            camera_info['camera_make'] = exif_data[271]
                        if 272 in exif_data:  # Model  
                            camera_info['camera_model'] = exif_data[272]
                        if camera_info:
                            metadata['camera_info'] = camera_info
                
                print(f"✅ Image processed: {width}x{height}, thumbnail created")
                return metadata
                
        except Exception as e:
            print(f"❌ Error processing image: {e}")
            return {'error': str(e), 'processed_at': datetime.now().isoformat()}
    
    async def _process_document(self, file_path: Path, uploaded_file: UploadedFile) -> Dict[str, Any]:
        """Document processing - CSV parsing, PDF info, etc."""
        print(f"📄 Processing document: {file_path}")
        
        try:
            metadata = {
                'processed_at': datetime.now().isoformat()
            }
            
            if uploaded_file.mime_type == 'text/csv':
                # CSV file analysis
                df = pd.read_csv(file_path)
                metadata.update({
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'columns': list(df.columns),
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                })
                
                print(f"✅ CSV processed: {len(df)} rows, {len(df.columns)} columns")
                
            elif uploaded_file.mime_type in [
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ]:
                # Excel file analysis
                df = pd.read_excel(file_path)
                metadata.update({
                    'row_count': len(df),
                    'column_count': len(df.columns), 
                    'columns': list(df.columns),
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                })
                
                print(f"✅ Excel processed: {len(df)} rows, {len(df.columns)} columns")
                
            elif uploaded_file.mime_type == 'application/pdf':
                # PDF info (would need PyPDF2 for full parsing)
                metadata.update({
                    'pages': 'Unknown',  # Would extract with PyPDF2
                    'size_mb': round(uploaded_file.file_size / (1024 * 1024), 2)
                })
                
                print(f"✅ PDF processed: {metadata['size_mb']} MB")
            
            return metadata
            
        except Exception as e:
            print(f"❌ Error processing document: {e}")
            return {'error': str(e), 'processed_at': datetime.now().isoformat()}
    
    async def create_product_image(
        self, 
        product_id: str, 
        file_id: str,
        alt_text: str,
        is_primary: bool = False
    ) -> ProductImage:
        """Product के लिए image association create करता है"""
        
        uploaded_file = self.uploaded_files.get(file_id)
        if not uploaded_file:
            raise ValueError(f"File not found: {file_id}")
        
        if uploaded_file.mime_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError("File is not an image")
        
        # Generate URLs
        base_url = "http://localhost:4026"  # Would be proper domain in production
        file_url = f"{base_url}/files/{file_id}"
        
        thumbnail_path = uploaded_file.metadata.get('thumbnail_path', '')
        thumbnail_filename = Path(thumbnail_path).name if thumbnail_path else ''
        thumbnail_url = f"{base_url}/thumbnails/{thumbnail_filename}" if thumbnail_filename else file_url
        
        # Get next display order
        existing_images = [img for img in self.product_images.values() if img.product_id == product_id]
        display_order = len(existing_images) + 1
        
        product_image = ProductImage(
            id=str(uuid.uuid4()),
            product_id=product_id,
            file_id=file_id,
            alt_text=alt_text,
            is_primary=is_primary,
            display_order=display_order,
            url=file_url,
            thumbnail_url=thumbnail_url
        )
        
        # If this is primary, make others non-primary
        if is_primary:
            for img in existing_images:
                if img.is_primary:
                    img.is_primary = False
        
        self.product_images[product_image.id] = product_image
        
        print(f"🖼️ Product image created: {product_id} - {alt_text}")
        return product_image
    
    async def process_bulk_import(self, file_id: str, job_type: str) -> BulkImportJob:
        """Bulk import job create करता है CSV/Excel data के लिए"""
        
        uploaded_file = self.uploaded_files.get(file_id)
        if not uploaded_file:
            raise ValueError(f"File not found: {file_id}")
        
        if uploaded_file.mime_type not in ['text/csv', 'application/vnd.ms-excel', 
                                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            raise ValueError("File must be CSV or Excel")
        
        # Create job
        job_id = str(uuid.uuid4())
        total_records = uploaded_file.metadata.get('row_count', 0)
        
        bulk_job = BulkImportJob(
            id=job_id,
            file_id=file_id,
            job_type=job_type,
            status='processing',
            total_records=total_records,
            processed_records=0,
            success_count=0,
            error_count=0,
            errors=[],
            created_at=datetime.now()
        )
        
        self.bulk_import_jobs[job_id] = bulk_job
        
        # Start async processing
        asyncio.create_task(self._process_bulk_job(bulk_job))
        
        print(f"📊 Bulk import job created: {job_id} ({job_type})")
        return bulk_job
    
    async def _process_bulk_job(self, job: BulkImportJob):
        """Background task for processing bulk import"""
        print(f"🔄 Processing bulk import job: {job.id}")
        
        try:
            uploaded_file = self.uploaded_files[job.file_id]
            file_path = Path(uploaded_file.file_path)
            
            # Read data
            if uploaded_file.mime_type == 'text/csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    await asyncio.sleep(0.1)  # Simulate processing time
                    
                    # Simulate different job types
                    if job.job_type == 'products':
                        # Validate product data
                        if pd.isna(row.get('name')) or pd.isna(row.get('price')):
                            raise ValueError("Missing required fields: name or price")
                        
                        # Create product (simulation)
                        print(f"Creating product: {row.get('name')}")
                        
                    elif job.job_type == 'inventory':
                        # Validate inventory data
                        if pd.isna(row.get('product_id')) or pd.isna(row.get('quantity')):
                            raise ValueError("Missing required fields: product_id or quantity")
                        
                        # Update inventory (simulation)
                        print(f"Updating inventory: {row.get('product_id')} -> {row.get('quantity')}")
                    
                    job.success_count += 1
                    
                except Exception as row_error:
                    job.error_count += 1
                    job.errors.append({
                        'row': index + 1,
                        'error': str(row_error),
                        'data': row.to_dict()
                    })
                    
                    print(f"❌ Row {index + 1} error: {row_error}")
                
                job.processed_records += 1
                
                # Update status periodically
                if job.processed_records % 10 == 0:
                    print(f"📊 Progress: {job.processed_records}/{job.total_records}")
            
            # Complete job
            job.status = 'completed'
            job.completed_at = datetime.now()
            
            print(f"✅ Bulk import completed: {job.success_count} success, {job.error_count} errors")
            
        except Exception as e:
            job.status = 'failed'
            job.errors.append({
                'row': 0,
                'error': f"Job failed: {str(e)}",
                'data': {}
            })
            job.completed_at = datetime.now()
            
            print(f"❌ Bulk import job failed: {e}")

# File storage instance
file_service = FileStorageService()

# GraphQL Types
class FileType(ObjectType):
    id = String()
    filename = String()
    original_name = String()
    file_size = Int()
    mime_type = String()
    uploaded_at = String()
    uploaded_by = String()
    url = String()
    metadata = String()  # JSON string
    
    def resolve_url(self, info):
        return f"http://localhost:4026/files/{self.id}"
    
    def resolve_metadata(self, info):
        return json.dumps(self.metadata) if self.metadata else None

class ProductImageType(ObjectType):
    id = String()
    product_id = String()
    file_id = String()
    alt_text = String()
    is_primary = Boolean()
    display_order = Int()
    url = String()
    thumbnail_url = String()
    
    file = Field(FileType)
    
    def resolve_file(self, info):
        return file_service.uploaded_files.get(self.file_id)

class SellerDocumentType(ObjectType):
    id = String()
    seller_id = String()
    document_type = String()
    file_id = String()
    status = String()
    uploaded_at = String()
    verified_at = String()
    
    file = Field(FileType)
    
    def resolve_file(self, info):
        return file_service.uploaded_files.get(self.file_id)

class BulkImportJobType(ObjectType):
    id = String()
    file_id = String()
    job_type = String()
    status = String()
    total_records = Int()
    processed_records = Int()
    success_count = Int()
    error_count = Int()
    errors = String()  # JSON string
    created_at = String()
    completed_at = String()
    progress_percentage = Float()
    
    file = Field(FileType)
    
    def resolve_file(self, info):
        return file_service.uploaded_files.get(self.file_id)
    
    def resolve_errors(self, info):
        return json.dumps(self.errors)
    
    def resolve_progress_percentage(self, info):
        if self.total_records == 0:
            return 0.0
        return round((self.processed_records / self.total_records) * 100, 2)

# Upload Mutations
class UploadFile(Mutation):
    class Arguments:
        file = Upload(required=True)
        category = String(default_value="general")
    
    success = Boolean()
    file = Field(FileType)
    message = String()
    
    async def mutate(self, info, file, category):
        try:
            context = info.context
            user_id = context.get('user_id', 'anonymous')
            
            uploaded_file = await file_service.save_file(file, category, user_id)
            
            return UploadFile(
                success=True,
                file=uploaded_file,
                message=f"File uploaded successfully: {uploaded_file.original_name}"
            )
            
        except Exception as e:
            return UploadFile(
                success=False,
                file=None,
                message=f"Upload failed: {str(e)}"
            )

class CreateProductImage(Mutation):
    class Arguments:
        product_id = String(required=True)
        file_id = String(required=True)
        alt_text = String(required=True)
        is_primary = Boolean(default_value=False)
    
    success = Boolean()
    product_image = Field(ProductImageType)
    message = String()
    
    async def mutate(self, info, product_id, file_id, alt_text, is_primary):
        try:
            product_image = await file_service.create_product_image(
                product_id, file_id, alt_text, is_primary
            )
            
            return CreateProductImage(
                success=True,
                product_image=product_image,
                message="Product image created successfully"
            )
            
        except Exception as e:
            return CreateProductImage(
                success=False,
                product_image=None,
                message=f"Failed to create product image: {str(e)}"
            )

class StartBulkImport(Mutation):
    class Arguments:
        file_id = String(required=True)
        job_type = String(required=True)  # products, inventory, pricing
    
    success = Boolean()
    job = Field(BulkImportJobType)
    message = String()
    
    async def mutate(self, info, file_id, job_type):
        try:
            job = await file_service.process_bulk_import(file_id, job_type)
            
            return StartBulkImport(
                success=True,
                job=job,
                message="Bulk import job started successfully"
            )
            
        except Exception as e:
            return StartBulkImport(
                success=False,
                job=None,
                message=f"Failed to start bulk import: {str(e)}"
            )

class UploadMultipleFiles(Mutation):
    class Arguments:
        files = List(Upload, required=True)
        category = String(default_value="general")
    
    success = Boolean()
    files = List(FileType)
    message = String()
    uploaded_count = Int()
    failed_count = Int()
    
    async def mutate(self, info, files, category):
        uploaded_files = []
        failed_uploads = 0
        
        context = info.context
        user_id = context.get('user_id', 'anonymous')
        
        for file in files:
            try:
                uploaded_file = await file_service.save_file(file, category, user_id)
                uploaded_files.append(uploaded_file)
            except Exception as e:
                failed_uploads += 1
                print(f"❌ Failed to upload {file.filename}: {e}")
        
        return UploadMultipleFiles(
            success=len(uploaded_files) > 0,
            files=uploaded_files,
            message=f"Uploaded {len(uploaded_files)} files, {failed_uploads} failed",
            uploaded_count=len(uploaded_files),
            failed_count=failed_uploads
        )

# Query and Mutations
class Query(ObjectType):
    files = List(FileType)
    file = Field(FileType, id=String(required=True))
    
    product_images = List(ProductImageType, product_id=String())
    product_image = Field(ProductImageType, id=String(required=True))
    
    seller_documents = List(SellerDocumentType, seller_id=String())
    
    bulk_import_jobs = List(BulkImportJobType)
    bulk_import_job = Field(BulkImportJobType, id=String(required=True))
    
    # File statistics
    upload_stats = Field(String)
    
    def resolve_files(self, info):
        return list(file_service.uploaded_files.values())
    
    def resolve_file(self, info, id):
        return file_service.uploaded_files.get(id)
    
    def resolve_product_images(self, info, product_id=None):
        images = list(file_service.product_images.values())
        if product_id:
            images = [img for img in images if img.product_id == product_id]
        return images
    
    def resolve_product_image(self, info, id):
        return file_service.product_images.get(id)
    
    def resolve_seller_documents(self, info, seller_id=None):
        docs = list(file_service.seller_documents.values())
        if seller_id:
            docs = [doc for doc in docs if doc.seller_id == seller_id]
        return docs
    
    def resolve_bulk_import_jobs(self, info):
        return list(file_service.bulk_import_jobs.values())
    
    def resolve_bulk_import_job(self, info, id):
        return file_service.bulk_import_jobs.get(id)
    
    def resolve_upload_stats(self, info):
        total_files = len(file_service.uploaded_files)
        total_size = sum(f.file_size for f in file_service.uploaded_files.values())
        image_count = sum(1 for f in file_service.uploaded_files.values() if f.mime_type in ALLOWED_IMAGE_TYPES)
        doc_count = sum(1 for f in file_service.uploaded_files.values() if f.mime_type in ALLOWED_DOCUMENT_TYPES)
        
        stats = {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'image_count': image_count,
            'document_count': doc_count,
            'product_images': len(file_service.product_images),
            'bulk_jobs': len(file_service.bulk_import_jobs)
        }
        
        return json.dumps(stats)

class Mutations(ObjectType):
    upload_file = UploadFile.Field()
    upload_multiple_files = UploadMultipleFiles.Field()
    create_product_image = CreateProductImage.Field()
    start_bulk_import = StartBulkImport.Field()

# GraphQL Schema
schema = Schema(query=Query, mutation=Mutations)

# FastAPI App
app = FastAPI(title="GraphQL File Upload System")

# Serve uploaded files
app.mount("/files", StaticFiles(directory=UPLOAD_DIR / "products"), name="files")
app.mount("/thumbnails", StaticFiles(directory=UPLOAD_DIR / "thumbnails"), name="thumbnails")
app.mount("/documents", StaticFiles(directory=UPLOAD_DIR / "documents"), name="documents")

# Context function
async def get_context(request: Request):
    return {
        'request': request,
        'user_id': request.headers.get('x-user-id', 'anonymous'),
        'user_role': request.headers.get('x-user-role', 'customer')
    }

# GraphQL endpoint
app.add_route("/graphql", GraphQLApp(schema=schema, context_value=get_context))

# File upload form (HTML interface for testing)
@app.get("/upload-form", response_class=HTMLResponse)
async def upload_form():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GraphQL File Upload Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .form-section { margin: 20px 0; padding: 20px; border: 1px solid #ccc; }
            input, select, button { margin: 5px; padding: 8px; }
            button { background: #007cba; color: white; border: none; cursor: pointer; }
            button:hover { background: #005a87; }
            .result { margin: 10px 0; padding: 10px; background: #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>🇮🇳 भारतीय E-commerce File Upload System</h1>
        
        <div class="form-section">
            <h2>📸 Product Image Upload</h2>
            <form id="imageForm">
                <input type="file" id="imageFile" accept="image/*" required>
                <input type="text" id="productId" placeholder="Product ID (e.g., PROD123)" required>
                <input type="text" id="altText" placeholder="Alt text (e.g., iPhone 15 Pro front view)" required>
                <label><input type="checkbox" id="isPrimary"> Primary Image</label><br>
                <button type="submit">Upload Product Image</button>
            </form>
            <div id="imageResult" class="result" style="display: none;"></div>
        </div>
        
        <div class="form-section">
            <h2>📄 Seller Document Upload</h2>
            <form id="docForm">
                <input type="file" id="docFile" accept=".pdf,.csv,.xlsx,.xls" required>
                <select id="docType">
                    <option value="gst_certificate">GST Certificate</option>
                    <option value="pan_card">PAN Card</option>
                    <option value="bank_details">Bank Account Details</option>
                    <option value="address_proof">Address Proof</option>
                </select>
                <input type="text" id="sellerId" placeholder="Seller ID" required>
                <button type="submit">Upload Document</button>
            </form>
            <div id="docResult" class="result" style="display: none;"></div>
        </div>
        
        <div class="form-section">
            <h2>📊 Bulk Import (CSV/Excel)</h2>
            <form id="bulkForm">
                <input type="file" id="bulkFile" accept=".csv,.xlsx,.xls" required>
                <select id="importType">
                    <option value="products">Products Import</option>
                    <option value="inventory">Inventory Update</option>
                    <option value="pricing">Price Update</option>
                </select>
                <button type="submit">Start Bulk Import</button>
            </form>
            <div id="bulkResult" class="result" style="display: none;"></div>
        </div>
        
        <div class="form-section">
            <h2>📈 Upload Statistics</h2>
            <button onclick="loadStats()">Refresh Stats</button>
            <div id="stats" class="result"></div>
        </div>
        
        <script>
            // GraphQL queries and mutations
            async function graphqlRequest(query, variables = {}) {
                const response = await fetch('/graphql', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-User-ID': 'demo-user',
                        'X-User-Role': 'seller'
                    },
                    body: JSON.stringify({ query, variables })
                });
                return response.json();
            }
            
            // Image upload handler
            document.getElementById('imageForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const file = document.getElementById('imageFile').files[0];
                const productId = document.getElementById('productId').value;
                const altText = document.getElementById('altText').value;
                const isPrimary = document.getElementById('isPrimary').checked;
                
                try {
                    // First upload file
                    const uploadMutation = `
                        mutation UploadFile($file: Upload!, $category: String!) {
                            uploadFile(file: $file, category: $category) {
                                success
                                file { id filename originalName }
                                message
                            }
                        }
                    `;
                    
                    const uploadResult = await graphqlRequest(uploadMutation, {
                        file: file,
                        category: "products"
                    });
                    
                    if (uploadResult.data.uploadFile.success) {
                        const fileId = uploadResult.data.uploadFile.file.id;
                        
                        // Then create product image
                        const imageMutation = `
                            mutation CreateProductImage($productId: String!, $fileId: String!, $altText: String!, $isPrimary: Boolean!) {
                                createProductImage(productId: $productId, fileId: $fileId, altText: $altText, isPrimary: $isPrimary) {
                                    success
                                    productImage { id url thumbnailUrl }
                                    message
                                }
                            }
                        `;
                        
                        const imageResult = await graphqlRequest(imageMutation, {
                            productId, fileId, altText, isPrimary
                        });
                        
                        document.getElementById('imageResult').style.display = 'block';
                        document.getElementById('imageResult').innerHTML = 
                            `<strong>✅ Success:</strong> ${imageResult.data.createProductImage.message}`;
                    }
                } catch (error) {
                    document.getElementById('imageResult').style.display = 'block';
                    document.getElementById('imageResult').innerHTML = 
                        `<strong>❌ Error:</strong> ${error.message}`;
                }
            });
            
            // Load statistics
            async function loadStats() {
                const query = `
                    query {
                        uploadStats
                    }
                `;
                
                try {
                    const result = await graphqlRequest(query);
                    const stats = JSON.parse(result.data.uploadStats);
                    
                    document.getElementById('stats').innerHTML = `
                        <h3>📊 Upload Statistics</h3>
                        <p><strong>Total Files:</strong> ${stats.total_files}</p>
                        <p><strong>Total Size:</strong> ${stats.total_size_mb} MB</p>
                        <p><strong>Images:</strong> ${stats.image_count}</p>
                        <p><strong>Documents:</strong> ${stats.document_count}</p>
                        <p><strong>Product Images:</strong> ${stats.product_images}</p>
                        <p><strong>Bulk Jobs:</strong> ${stats.bulk_jobs}</p>
                    `;
                } catch (error) {
                    document.getElementById('stats').innerHTML = 
                        `<strong>❌ Error loading stats:</strong> ${error.message}`;
                }
            }
            
            // Load initial stats
            loadStats();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Health check
@app.get("/health")
async def health_check():
    return {
        "service": "graphql-file-upload",
        "status": "healthy",
        "upload_stats": {
            "total_files": len(file_service.uploaded_files),
            "total_size_mb": round(sum(f.file_size for f in file_service.uploaded_files.values()) / (1024 * 1024), 2),
            "storage_directories": ["products", "sellers", "documents", "bulk", "thumbnails"]
        },
        "supported_formats": {
            "images": list(ALLOWED_IMAGE_TYPES),
            "documents": list(ALLOWED_DOCUMENT_TYPES)
        },
        "features": [
            "Multi-format image support (including HEIC from iPhone)",
            "Automatic thumbnail generation", 
            "Bulk CSV/Excel import",
            "Document processing",
            "File metadata extraction",
            "Progress tracking"
        ]
    }

# File serving endpoint
@app.get("/file/{file_id}")
async def serve_file(file_id: str):
    uploaded_file = file_service.uploaded_files.get(file_id)
    if not uploaded_file:
        raise HTTPException(404, "File not found")
    
    file_path = Path(uploaded_file.file_path)
    if not file_path.exists():
        raise HTTPException(404, "File not found on disk")
    
    return FileResponse(file_path, filename=uploaded_file.original_name)

@app.get("/")
async def root():
    return {
        "title": "GraphQL File Upload System",
        "description": "File upload system for Indian e-commerce with GraphQL",
        "endpoints": {
            "/graphql": "GraphQL endpoint",
            "/upload-form": "Web interface for testing uploads",
            "/health": "Health check",
            "/files/{file_id}": "Serve uploaded files"
        },
        "features": {
            "image_upload": "Product images with automatic thumbnail generation",
            "document_upload": "Seller verification documents",
            "bulk_import": "CSV/Excel bulk data import",
            "file_processing": "Automatic metadata extraction",
            "indian_context": "Support for HEIC images from iPhone, Indian document types"
        },
        "sample_mutations": {
            "upload_file": """
                mutation UploadFile($file: Upload!, $category: String!) {
                    uploadFile(file: $file, category: $category) {
                        success
                        file { id filename originalName url }
                        message
                    }
                }
            """,
            "create_product_image": """
                mutation CreateProductImage($productId: String!, $fileId: String!, $altText: String!) {
                    createProductImage(productId: $productId, fileId: $fileId, altText: $altText) {
                        success
                        productImage { id url thumbnailUrl }
                        message
                    }
                }
            """,
            "bulk_import": """
                mutation StartBulkImport($fileId: String!, $jobType: String!) {
                    startBulkImport(fileId: $fileId, jobType: $jobType) {
                        success
                        job { id status progressPercentage }
                        message
                    }
                }
            """
        }
    }

if __name__ == "__main__":
    print("📁 Starting GraphQL File Upload Server...")
    print("🇮🇳 Features for Indian E-commerce:")
    print("   - Product image uploads with thumbnails")
    print("   - Seller document verification")
    print("   - Bulk CSV/Excel import")
    print("   - HEIC image support (iPhone photos)")
    print("   - Multi-language file naming support")
    print("\n🔧 Upload Directories:")
    for directory in ["products", "sellers", "documents", "bulk", "thumbnails"]:
        print(f"   - {UPLOAD_DIR / directory}")
    
    print(f"\n🌐 Web Interface: http://localhost:4026/upload-form")
    print("📊 GraphQL Playground: http://localhost:4026/graphql")
    
    uvicorn.run(
        "12_file_upload_graphql:app",
        host="0.0.0.0",
        port=4026,
        reload=True,
        log_level="info"
    )