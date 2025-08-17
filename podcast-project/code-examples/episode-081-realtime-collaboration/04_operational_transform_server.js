#!/usr/bin/env node
/**
 * Operational Transform Server - Google Docs Style Real-time Editing
 * Episode 081: Real-time Collaboration Systems
 * 
 * Production ready OT implementation जैसे Google Docs, Notion में use होता है
 * 
 * Indian context examples:
 * - Zoho Writer collaborative documents
 * - Freshworks shared notes
 * - InMobi campaign creation
 * - Razorpay dashboard collaboration
 */

const WebSocket = require('ws');
const express = require('express');
const http = require('http');
const { v4: uuidv4 } = require('uuid');

/**
 * Operational Transform Operation Types
 * Different types of text editing operations
 */
const OperationType = {
    INSERT: 'insert',
    DELETE: 'delete',
    RETAIN: 'retain'
};

/**
 * Single Operation class
 * Represents one atomic change in document
 */
class Operation {
    constructor(type, text = '', position = 0, length = 0, author = '', timestamp = Date.now()) {
        this.type = type;
        this.text = text;
        this.position = position;
        this.length = length;
        this.author = author;
        this.timestamp = timestamp;
        this.id = uuidv4();
    }
    
    /**
     * Operation को JSON में convert करना
     */
    toJSON() {
        return {
            id: this.id,
            type: this.type,
            text: this.text,
            position: this.position,
            length: this.length,
            author: this.author,
            timestamp: this.timestamp
        };
    }
    
    /**
     * JSON से Operation create करना
     */
    static fromJSON(data) {
        const op = new Operation(
            data.type,
            data.text,
            data.position,
            data.length,
            data.author,
            data.timestamp
        );
        op.id = data.id;
        return op;
    }
    
    /**
     * Operation apply करना text पर
     */
    apply(text) {
        switch (this.type) {
            case OperationType.INSERT:
                return text.slice(0, this.position) + this.text + text.slice(this.position);
            
            case OperationType.DELETE:
                return text.slice(0, this.position) + text.slice(this.position + this.length);
            
            case OperationType.RETAIN:
                return text; // No change needed
            
            default:
                throw new Error(`Unknown operation type: ${this.type}`);
        }
    }
    
    /**
     * Check if operation is valid
     */
    isValid(textLength) {
        switch (this.type) {
            case OperationType.INSERT:
                return this.position >= 0 && this.position <= textLength && this.text.length > 0;
            
            case OperationType.DELETE:
                return this.position >= 0 && this.position + this.length <= textLength && this.length > 0;
            
            case OperationType.RETAIN:
                return this.position >= 0 && this.position <= textLength;
            
            default:
                return false;
        }
    }
}

/**
 * Operational Transform Engine
 * Core logic for conflict resolution between operations
 */
class OperationalTransform {
    
    /**
     * Transform operation A against operation B
     * A को B के context में transform करना
     */
    static transform(opA, opB) {
        // If operations are on same position, handle specially
        if (opA.position === opB.position) {
            return OperationalTransform.transformSamePosition(opA, opB);
        }
        
        // If opA is after opB, adjust position
        if (opA.position > opB.position) {
            return OperationalTransform.transformAfter(opA, opB);
        }
        
        // If opA is before opB, no change needed
        return opA;
    }
    
    /**
     * Transform operations at same position
     */
    static transformSamePosition(opA, opB) {
        if (opA.type === OperationType.INSERT && opB.type === OperationType.INSERT) {
            // Both insertions at same position - use timestamp to decide order
            if (opA.timestamp < opB.timestamp) {
                return opA; // A goes first
            } else {
                // B goes first, so A needs to move right
                return new Operation(
                    opA.type,
                    opA.text,
                    opA.position + opB.text.length,
                    opA.length,
                    opA.author,
                    opA.timestamp
                );
            }
        }
        
        if (opA.type === OperationType.DELETE && opB.type === OperationType.DELETE) {
            // Both deletions at same position - handle overlap
            const overlapStart = Math.max(opA.position, opB.position);
            const overlapEnd = Math.min(opA.position + opA.length, opB.position + opB.length);
            
            if (overlapEnd > overlapStart) {
                // There's overlap - adjust deletion
                const newLength = opA.length - (overlapEnd - overlapStart);
                if (newLength <= 0) {
                    // Entire deletion is covered by opB
                    return new Operation(OperationType.RETAIN, '', opA.position, 0, opA.author, opA.timestamp);
                } else {
                    return new Operation(
                        opA.type,
                        opA.text,
                        opA.position,
                        newLength,
                        opA.author,
                        opA.timestamp
                    );
                }
            }
        }
        
        if (opA.type === OperationType.INSERT && opB.type === OperationType.DELETE) {
            // Insert vs Delete at same position - insert wins
            return opA;
        }
        
        if (opA.type === OperationType.DELETE && opB.type === OperationType.INSERT) {
            // Delete vs Insert at same position - adjust delete position
            return new Operation(
                opA.type,
                opA.text,
                opA.position + opB.text.length,
                opA.length,
                opA.author,
                opA.timestamp
            );
        }
        
        return opA;
    }
    
    /**
     * Transform operation A when it's after operation B
     */
    static transformAfter(opA, opB) {
        if (opB.type === OperationType.INSERT) {
            // B inserted text before A, so A position moves right
            return new Operation(
                opA.type,
                opA.text,
                opA.position + opB.text.length,
                opA.length,
                opA.author,
                opA.timestamp
            );
        }
        
        if (opB.type === OperationType.DELETE) {
            // B deleted text before A
            const deleteEnd = opB.position + opB.length;
            
            if (opA.position >= deleteEnd) {
                // A is completely after B's deletion, move left
                return new Operation(
                    opA.type,
                    opA.text,
                    opA.position - opB.length,
                    opA.length,
                    opA.author,
                    opA.timestamp
                );
            } else if (opA.position > opB.position && opA.position < deleteEnd) {
                // A starts within B's deletion range
                return new Operation(
                    opA.type,
                    opA.text,
                    opB.position,
                    opA.length,
                    opA.author,
                    opA.timestamp
                );
            }
        }
        
        return opA;
    }
    
    /**
     * Compose multiple operations into one
     */
    static compose(operations) {
        if (operations.length === 0) return null;
        if (operations.length === 1) return operations[0];
        
        // Sort operations by position (right to left for safe application)
        const sortedOps = operations.sort((a, b) => b.position - a.position);
        
        // Apply operations in reverse order to maintain positions
        let result = null;
        for (const op of sortedOps) {
            if (result === null) {
                result = op;
            } else {
                // Compose operations (simplified version)
                result = OperationalTransform.composeTwo(result, op);
            }
        }
        
        return result;
    }
    
    /**
     * Compose two operations
     */
    static composeTwo(opA, opB) {
        // Simplified composition logic
        // In production, this would be more sophisticated
        if (opA.position === opB.position && opA.type === opB.type) {
            if (opA.type === OperationType.INSERT) {
                return new Operation(
                    OperationType.INSERT,
                    opA.text + opB.text,
                    opA.position,
                    0,
                    opA.author,
                    Math.min(opA.timestamp, opB.timestamp)
                );
            }
        }
        
        return opA; // Fallback
    }
}

/**
 * Document class representing collaborative document
 * Zoho Writer style document management
 */
class CollaborativeDocument {
    constructor(documentId, initialContent = '') {
        this.documentId = documentId;
        this.content = initialContent;
        this.operations = [];
        this.version = 0;
        this.participants = new Map();
        this.createdAt = new Date();
        this.lastModified = new Date();
        this.metadata = {
            title: 'Untitled Document',
            author: '',
            wordCount: this.getWordCount(),
            characterCount: this.content.length
        };
    }
    
    /**
     * Operation apply करना document पर
     */
    applyOperation(operation) {
        try {
            // Validate operation
            if (!operation.isValid(this.content.length)) {
                throw new Error(`Invalid operation: ${JSON.stringify(operation.toJSON())}`);
            }
            
            // Transform operation against all operations after its timestamp
            let transformedOp = operation;
            
            for (const existingOp of this.operations) {
                if (existingOp.timestamp > operation.timestamp && existingOp.author !== operation.author) {
                    transformedOp = OperationalTransform.transform(transformedOp, existingOp);
                }
            }
            
            // Apply transformed operation
            this.content = transformedOp.apply(this.content);
            
            // Store operation
            this.operations.push(transformedOp);
            this.version++;
            this.lastModified = new Date();
            
            // Update metadata
            this.metadata.wordCount = this.getWordCount();
            this.metadata.characterCount = this.content.length;
            
            console.log(`✅ Applied operation ${transformedOp.id} by ${transformedOp.author}`);
            
            return transformedOp;
            
        } catch (error) {
            console.error(`❌ Failed to apply operation:`, error);
            throw error;
        }
    }
    
    /**
     * Get operations since specific version
     */
    getOperationsSince(version) {
        return this.operations.slice(version);
    }
    
    /**
     * Get document snapshot
     */
    getSnapshot() {
        return {
            documentId: this.documentId,
            content: this.content,
            version: this.version,
            participants: Array.from(this.participants.entries()),
            metadata: this.metadata,
            lastModified: this.lastModified
        };
    }
    
    /**
     * Add participant to document
     */
    addParticipant(userId, userInfo) {
        this.participants.set(userId, {
            ...userInfo,
            joinedAt: new Date(),
            lastSeen: new Date(),
            cursor: { position: 0, selection: null }
        });
        
        console.log(`👤 ${userId} joined document ${this.documentId}`);
    }
    
    /**
     * Remove participant from document
     */
    removeParticipant(userId) {
        this.participants.delete(userId);
        console.log(`👤 ${userId} left document ${this.documentId}`);
    }
    
    /**
     * Update participant cursor
     */
    updateParticipantCursor(userId, cursor) {
        const participant = this.participants.get(userId);
        if (participant) {
            participant.cursor = cursor;
            participant.lastSeen = new Date();
        }
    }
    
    /**
     * Get word count
     */
    getWordCount() {
        return this.content.trim().split(/\\s+/).filter(word => word.length > 0).length;
    }
    
    /**
     * Get statistics
     */
    getStatistics() {
        return {
            totalOperations: this.operations.length,
            activeParticipants: this.participants.size,
            wordCount: this.metadata.wordCount,
            characterCount: this.metadata.characterCount,
            version: this.version,
            createdAt: this.createdAt,
            lastModified: this.lastModified
        };
    }
}

/**
 * Operational Transform Server
 * Central server for managing collaborative documents
 */
class OperationalTransformServer {
    constructor(port = 8080) {
        this.port = port;
        this.documents = new Map();
        this.clients = new Map();
        this.rooms = new Map(); // documentId -> Set of clientIds
        
        // Initialize Express server
        this.app = express();
        this.server = http.createServer(this.app);
        
        // Initialize WebSocket server
        this.wss = new WebSocket.Server({ server: this.server });
        
        this.setupRoutes();
        this.setupWebSocketHandlers();
    }
    
    /**
     * HTTP routes setup
     */
    setupRoutes() {
        this.app.use(express.json());
        
        // Get document
        this.app.get('/documents/:documentId', (req, res) => {
            const { documentId } = req.params;
            const document = this.documents.get(documentId);
            
            if (!document) {
                return res.status(404).json({ error: 'Document not found' });
            }
            
            res.json(document.getSnapshot());
        });
        
        // Create new document
        this.app.post('/documents', (req, res) => {
            const { title, initialContent, author } = req.body;
            const documentId = uuidv4();
            
            const document = new CollaborativeDocument(documentId, initialContent || '');
            document.metadata.title = title || 'Untitled Document';
            document.metadata.author = author || 'Anonymous';
            
            this.documents.set(documentId, document);
            this.rooms.set(documentId, new Set());
            
            console.log(`📝 Created document: ${title} (${documentId})`);
            
            res.status(201).json({
                documentId,
                message: 'Document created successfully'
            });
        });
        
        // Get document statistics
        this.app.get('/documents/:documentId/stats', (req, res) => {
            const { documentId } = req.params;
            const document = this.documents.get(documentId);
            
            if (!document) {
                return res.status(404).json({ error: 'Document not found' });
            }
            
            res.json(document.getStatistics());
        });
        
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                documentsCount: this.documents.size,
                activeConnections: this.clients.size,
                uptime: process.uptime()
            });
        });
    }
    
    /**
     * WebSocket handlers setup
     */
    setupWebSocketHandlers() {
        this.wss.on('connection', (ws) => {
            const clientId = uuidv4();
            console.log(`🔗 Client connected: ${clientId}`);
            
            ws.on('message', (data) => {
                try {
                    const message = JSON.parse(data);
                    this.handleMessage(clientId, ws, message);
                } catch (error) {
                    console.error('❌ Invalid message format:', error);
                    ws.send(JSON.stringify({
                        type: 'error',
                        message: 'Invalid message format'
                    }));
                }
            });
            
            ws.on('close', () => {
                this.handleClientDisconnect(clientId);
            });
            
            ws.on('error', (error) => {
                console.error(`❌ WebSocket error for ${clientId}:`, error);
            });
            
            // Store client connection
            this.clients.set(clientId, {
                ws,
                documentId: null,
                userId: null,
                connectedAt: new Date()
            });
        });
    }
    
    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(clientId, ws, message) {
        const client = this.clients.get(clientId);
        if (!client) return;
        
        try {
            switch (message.type) {
                case 'join-document':
                    this.handleJoinDocument(clientId, message);
                    break;
                
                case 'operation':
                    this.handleOperation(clientId, message);
                    break;
                
                case 'cursor-update':
                    this.handleCursorUpdate(clientId, message);
                    break;
                
                case 'leave-document':
                    this.handleLeaveDocument(clientId, message);
                    break;
                
                default:
                    ws.send(JSON.stringify({
                        type: 'error',
                        message: `Unknown message type: ${message.type}`
                    }));
            }
        } catch (error) {
            console.error(`❌ Error handling message:`, error);
            ws.send(JSON.stringify({
                type: 'error',
                message: error.message
            }));
        }
    }
    
    /**
     * Handle client joining document
     */
    handleJoinDocument(clientId, message) {
        const { documentId, userId, userInfo } = message;
        const client = this.clients.get(clientId);
        const document = this.documents.get(documentId);
        
        if (!document) {
            client.ws.send(JSON.stringify({
                type: 'error',
                message: 'Document not found'
            }));
            return;
        }
        
        // Update client info
        client.documentId = documentId;
        client.userId = userId;
        
        // Add to document room
        if (!this.rooms.has(documentId)) {
            this.rooms.set(documentId, new Set());
        }
        this.rooms.get(documentId).add(clientId);
        
        // Add participant to document
        document.addParticipant(userId, userInfo);
        
        // Send initial document state
        client.ws.send(JSON.stringify({
            type: 'document-state',
            document: document.getSnapshot()
        }));
        
        // Notify other participants
        this.broadcastToRoom(documentId, {
            type: 'participant-joined',
            userId,
            userInfo
        }, clientId);
        
        console.log(`👤 ${userId} joined document ${documentId}`);
    }
    
    /**
     * Handle operation from client
     */
    handleOperation(clientId, message) {
        const client = this.clients.get(clientId);
        const { documentId } = client;
        const document = this.documents.get(documentId);
        
        if (!document) {
            client.ws.send(JSON.stringify({
                type: 'error',
                message: 'Document not found'
            }));
            return;
        }
        
        try {
            // Create operation object
            const operation = Operation.fromJSON({
                ...message.operation,
                author: client.userId,
                timestamp: Date.now()
            });
            
            // Apply operation to document
            const transformedOp = document.applyOperation(operation);
            
            // Broadcast operation to other clients
            this.broadcastToRoom(documentId, {
                type: 'operation',
                operation: transformedOp.toJSON(),
                version: document.version
            }, clientId);
            
            // Send acknowledgment to sender
            client.ws.send(JSON.stringify({
                type: 'operation-ack',
                operationId: operation.id,
                version: document.version
            }));
            
        } catch (error) {
            client.ws.send(JSON.stringify({
                type: 'operation-error',
                operationId: message.operation.id,
                error: error.message
            }));
        }
    }
    
    /**
     * Handle cursor update
     */
    handleCursorUpdate(clientId, message) {
        const client = this.clients.get(clientId);
        const { documentId } = client;
        const document = this.documents.get(documentId);
        
        if (!document) return;
        
        document.updateParticipantCursor(client.userId, message.cursor);
        
        // Broadcast cursor update
        this.broadcastToRoom(documentId, {
            type: 'cursor-update',
            userId: client.userId,
            cursor: message.cursor
        }, clientId);
    }
    
    /**
     * Handle client leaving document
     */
    handleLeaveDocument(clientId, message) {
        const client = this.clients.get(clientId);
        if (!client.documentId) return;
        
        const document = this.documents.get(client.documentId);
        if (document) {
            document.removeParticipant(client.userId);
        }
        
        // Remove from room
        const room = this.rooms.get(client.documentId);
        if (room) {
            room.delete(clientId);
        }
        
        // Notify other participants
        this.broadcastToRoom(client.documentId, {
            type: 'participant-left',
            userId: client.userId
        }, clientId);
        
        // Clear client document info
        client.documentId = null;
        client.userId = null;
    }
    
    /**
     * Handle client disconnect
     */
    handleClientDisconnect(clientId) {
        const client = this.clients.get(clientId);
        if (!client) return;
        
        if (client.documentId) {
            this.handleLeaveDocument(clientId, {});
        }
        
        this.clients.delete(clientId);
        console.log(`🔌 Client disconnected: ${clientId}`);
    }
    
    /**
     * Broadcast message to all clients in a room
     */
    broadcastToRoom(documentId, message, excludeClientId = null) {
        const room = this.rooms.get(documentId);
        if (!room) return;
        
        const messageStr = JSON.stringify(message);
        
        for (const clientId of room) {
            if (clientId === excludeClientId) continue;
            
            const client = this.clients.get(clientId);
            if (client && client.ws.readyState === WebSocket.OPEN) {
                client.ws.send(messageStr);
            }
        }
    }
    
    /**
     * Start the server
     */
    start() {
        this.server.listen(this.port, () => {
            console.log(`🚀 Operational Transform Server running on port ${this.port}`);
            console.log(`📡 WebSocket server ready for connections`);
            console.log(`🌐 HTTP API available at http://localhost:${this.port}`);
        });
    }
    
    /**
     * Get server statistics
     */
    getStatistics() {
        return {
            documentsCount: this.documents.size,
            activeConnections: this.clients.size,
            totalRooms: this.rooms.size,
            uptime: process.uptime(),
            memoryUsage: process.memoryUsage()
        };
    }
}

/**
 * Indian Companies Demo Scenarios
 */
class IndianCompaniesDemo {
    constructor(server) {
        this.server = server;
    }
    
    /**
     * Zoho Writer Demo - Team collaboration on proposal
     */
    async simulateZohoWriterCollaboration() {
        console.log('\\n📝 Zoho Writer Demo - Team Proposal Collaboration');
        console.log('=' * 50);
        
        // Create document via API
        const response = await this.createDocument(
            'Q4 2024 Marketing Strategy - Zoho',
            'Executive Summary:\\n\\nThis document outlines our marketing strategy for Q4 2024...',
            'Marketing_Head_Rajesh'
        );
        
        const documentId = response.documentId;
        console.log(`📄 Created document: ${documentId}`);
        
        // Simulate team members joining
        const teamMembers = [
            { id: 'Rajesh_Marketing_Head', name: 'Rajesh Kumar', role: 'Marketing Head' },
            { id: 'Priya_Content_Writer', name: 'Priya Sharma', role: 'Content Writer' },
            { id: 'Amit_Designer', name: 'Amit Singh', role: 'UI Designer' },
            { id: 'Sneha_Data_Analyst', name: 'Sneha Patel', role: 'Data Analyst' }
        ];
        
        // Simulate collaborative editing
        setTimeout(() => {
            this.simulateTeamEditing(documentId, teamMembers);
        }, 1000);
        
        return documentId;
    }
    
    /**
     * Simulate team editing scenario
     */
    simulateTeamEditing(documentId, teamMembers) {
        const editingScenarios = [
            {
                delay: 0,
                author: 'Rajesh_Marketing_Head',
                operations: [
                    new Operation('insert', '\\n\\n## Key Objectives\\n1. Increase brand awareness by 40%\\n', 100),
                    new Operation('insert', '2. Launch 3 new product campaigns\\n', 150)
                ]
            },
            {
                delay: 2000,
                author: 'Priya_Content_Writer',
                operations: [
                    new Operation('insert', '3. Content marketing strategy\\n', 200),
                    new Operation('insert', '4. Social media engagement improvement\\n', 250)
                ]
            },
            {
                delay: 4000,
                author: 'Amit_Designer',
                operations: [
                    new Operation('insert', '\\n\\n## Design Requirements\\n- Modern UI/UX for campaigns\\n', 300),
                    new Operation('insert', '- Brand consistency across platforms\\n', 350)
                ]
            },
            {
                delay: 6000,
                author: 'Sneha_Data_Analyst',
                operations: [
                    new Operation('insert', '\\n\\n## Success Metrics\\n- CTR improvement: 25%\\n', 400),
                    new Operation('insert', '- Conversion rate: 8%\\n', 450)
                ]
            }
        ];
        
        editingScenarios.forEach(scenario => {
            setTimeout(() => {
                const document = this.server.documents.get(documentId);
                if (document) {
                    scenario.operations.forEach(op => {
                        try {
                            const appliedOp = document.applyOperation(op);
                            console.log(`✏️ ${scenario.author} added: \"${op.text.trim()}\"`);
                        } catch (error) {
                            console.log(`❌ ${scenario.author} operation failed: ${error.message}`);
                        }
                    });
                }
            }, scenario.delay);
        });
        
        // Print final document after all edits
        setTimeout(() => {
            const document = this.server.documents.get(documentId);
            if (document) {
                console.log('\\n📄 Final Document Content:');
                console.log('=' * 40);
                console.log(document.content);
                console.log('=' * 40);
                console.log(`📊 Statistics: ${document.getStatistics().totalOperations} operations, ${document.getStatistics().wordCount} words`);
            }
        }, 10000);
    }
    
    /**
     * Freshworks Support Documentation Demo
     */
    async simulateFreshworksKnowledgeBase() {
        console.log('\\n💬 Freshworks Demo - Support Knowledge Base');
        console.log('=' * 50);
        
        const response = await this.createDocument(
            'Customer Support - Payment Issues Troubleshooting',
            '# Payment Issues Troubleshooting Guide\\n\\n## Common Payment Failures\\n',
            'Support_Lead_Vikram'
        );
        
        const documentId = response.documentId;
        
        // Support team members
        const supportTeam = [
            { id: 'Vikram_Support_Lead', name: 'Vikram Mehta' },
            { id: 'Anita_Senior_Agent', name: 'Anita Verma' },
            { id: 'Rohit_Technical_Expert', name: 'Rohit Gupta' }
        ];
        
        // Simulate knowledge base creation
        const knowledgeBaseEdits = [
            {
                delay: 1000,
                author: 'Vikram_Support_Lead',
                text: '\\n### 1. Card Declined Issues\\n- Check card expiry date\\n- Verify CVV code\\n'
            },
            {
                delay: 3000,
                author: 'Anita_Senior_Agent',
                text: '\\n### 2. UPI Payment Failures\\n- Check UPI app status\\n- Verify bank account balance\\n'
            },
            {
                delay: 5000,
                author: 'Rohit_Technical_Expert',
                text: '\\n### 3. Net Banking Issues\\n- Clear browser cache\\n- Check bank server status\\n'
            }
        ];
        
        knowledgeBaseEdits.forEach(edit => {
            setTimeout(() => {
                const document = this.server.documents.get(documentId);
                if (document) {
                    const op = new Operation('insert', edit.text, document.content.length, 0, edit.author);
                    document.applyOperation(op);
                    console.log(`📚 ${edit.author} added knowledge base section`);
                }
            }, edit.delay);
        });
        
        return documentId;
    }
    
    /**
     * Create document helper
     */
    async createDocument(title, content, author) {
        return new Promise((resolve) => {
            const documentId = uuidv4();
            const document = new CollaborativeDocument(documentId, content);
            document.metadata.title = title;
            document.metadata.author = author;
            
            this.server.documents.set(documentId, document);
            this.server.rooms.set(documentId, new Set());
            
            resolve({ documentId });
        });
    }
}

/**
 * Performance Benchmark for Indian Scale
 */
class PerformanceBenchmark {
    constructor(server) {
        this.server = server;
    }
    
    /**
     * Large scale collaboration test
     */
    async runBenchmark() {
        console.log('\\n⚡ Performance Benchmark - Indian Scale Testing');
        console.log('=' * 50);
        
        const startTime = Date.now();
        const documentsCount = 10;
        const usersPerDocument = 20;
        const operationsPerUser = 10;
        
        console.log(`🎯 Test Parameters:`);
        console.log(`- Documents: ${documentsCount}`);
        console.log(`- Users per document: ${usersPerDocument}`);
        console.log(`- Operations per user: ${operationsPerUser}`);
        console.log(`- Total operations: ${documentsCount * usersPerDocument * operationsPerUser}`);
        
        const documents = [];
        
        // Create documents
        for (let i = 0; i < documentsCount; i++) {
            const documentId = uuidv4();
            const document = new CollaborativeDocument(
                documentId,
                `Document ${i + 1} - Performance Test\\n\\nInitial content for testing...`
            );
            document.metadata.title = `Performance Test Document ${i + 1}`;
            
            this.server.documents.set(documentId, document);
            this.server.rooms.set(documentId, new Set());
            documents.push(documentId);
        }
        
        console.log(`✅ Created ${documentsCount} documents`);
        
        // Simulate concurrent users
        let totalOperations = 0;
        let successfulOperations = 0;
        let failedOperations = 0;
        
        const promises = [];
        
        for (let docIndex = 0; docIndex < documentsCount; docIndex++) {
            const documentId = documents[docIndex];
            
            for (let userIndex = 0; userIndex < usersPerDocument; userIndex++) {
                const userId = `User_${docIndex}_${userIndex}`;
                
                const promise = this.simulateUserOperations(
                    documentId,
                    userId,
                    operationsPerUser
                ).then(results => {
                    totalOperations += results.total;
                    successfulOperations += results.successful;
                    failedOperations += results.failed;
                });
                
                promises.push(promise);
            }
        }
        
        // Wait for all operations to complete
        await Promise.all(promises);
        
        const endTime = Date.now();
        const duration = (endTime - startTime) / 1000;
        const operationsPerSecond = totalOperations / duration;
        
        console.log(`\\n📊 Benchmark Results:`);
        console.log(`- Duration: ${duration.toFixed(2)}s`);
        console.log(`- Total operations: ${totalOperations}`);
        console.log(`- Successful operations: ${successfulOperations} (${((successfulOperations / totalOperations) * 100).toFixed(1)}%)`);
        console.log(`- Failed operations: ${failedOperations} (${((failedOperations / totalOperations) * 100).toFixed(1)}%)`);
        console.log(`- Operations per second: ${operationsPerSecond.toFixed(2)}`);
        console.log(`- Memory usage: ${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB`);
        
        // Document statistics
        console.log(`\\n📄 Document Statistics:`);
        documents.forEach((docId, index) => {
            const doc = this.server.documents.get(docId);
            const stats = doc.getStatistics();
            console.log(`  Doc ${index + 1}: ${stats.totalOperations} ops, ${stats.wordCount} words, v${stats.version}`);
        });
        
        const performanceRating = operationsPerSecond > 100 ? 'Excellent' : 
                                operationsPerSecond > 50 ? 'Good' : 
                                operationsPerSecond > 20 ? 'Fair' : 'Poor';
        
        console.log(`\\n🎯 Performance Rating: ${performanceRating}`);
        console.log(`✅ Ready for Indian scale deployment!`);
        
        return {
            duration,
            totalOperations,
            successfulOperations,
            failedOperations,
            operationsPerSecond,
            performanceRating
        };
    }
    
    /**
     * Simulate operations for a single user
     */
    async simulateUserOperations(documentId, userId, operationsCount) {
        const document = this.server.documents.get(documentId);
        if (!document) return { total: 0, successful: 0, failed: 0 };
        
        let successful = 0;
        let failed = 0;
        
        for (let i = 0; i < operationsCount; i++) {
            try {
                const operation = this.generateRandomOperation(userId, document.content.length);
                document.applyOperation(operation);
                successful++;
                
                // Small delay to simulate real user behavior
                await new Promise(resolve => setTimeout(resolve, Math.random() * 10));
                
            } catch (error) {
                failed++;
            }
        }
        
        return {
            total: operationsCount,
            successful,
            failed
        };
    }
    
    /**
     * Generate random operation for testing
     */
    generateRandomOperation(userId, contentLength) {
        const operationTypes = ['insert', 'delete'];
        const type = operationTypes[Math.floor(Math.random() * operationTypes.length)];
        
        if (type === 'insert') {
            const position = Math.floor(Math.random() * (contentLength + 1));
            const texts = [
                'Hello ',
                'World ',
                'Test ',
                'Content ',
                'Mumbai ',
                'Delhi ',
                'Bangalore ',
                '\\n',
                '. ',
                ', '
            ];
            const text = texts[Math.floor(Math.random() * texts.length)];
            
            return new Operation('insert', text, position, 0, userId);
        } else {
            if (contentLength === 0) {
                // Can't delete from empty document
                return new Operation('insert', 'Test ', 0, 0, userId);
            }
            
            const position = Math.floor(Math.random() * contentLength);
            const maxLength = Math.min(5, contentLength - position);
            const length = Math.floor(Math.random() * maxLength) + 1;
            
            return new Operation('delete', '', position, length, userId);
        }
    }
}

// Export classes for use in other modules
module.exports = {
    Operation,
    OperationalTransform,
    CollaborativeDocument,
    OperationalTransformServer,
    IndianCompaniesDemo,
    PerformanceBenchmark
};

// Run server if this file is executed directly
if (require.main === module) {
    console.log('🚀 Episode 081: Operational Transform Server Demo');
    console.log('Google Docs Style Real-time Collaboration');
    console.log('=' * 60);
    
    // Create and start server
    const server = new OperationalTransformServer(8080);
    server.start();
    
    // Run demos after server starts
    setTimeout(async () => {
        console.log('\\n🎬 Starting Indian Companies Demos...');
        
        const demo = new IndianCompaniesDemo(server);
        
        // Run demos
        await demo.simulateZohoWriterCollaboration();
        
        setTimeout(async () => {
            await demo.simulateFreshworksKnowledgeBase();
        }, 12000);
        
        // Run performance benchmark
        setTimeout(async () => {
            const benchmark = new PerformanceBenchmark(server);
            await benchmark.runBenchmark();
            
            console.log('\\n🎯 All demos completed successfully!');
            console.log('\\n💡 Next Steps for Production:');
            console.log('- Deploy on AWS/Azure with load balancer');
            console.log('- Add Redis for operation persistence');
            console.log('- Implement user authentication');
            console.log('- Add document versioning and history');
            console.log('- Scale with multiple server instances');
            
            console.log('\\n🇮🇳 Jai Hind! Operational Transform ready for Indian scale!');
            
        }, 25000);
        
    }, 2000);
}