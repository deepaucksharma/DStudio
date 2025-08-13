#!/usr/bin/env python3
"""
Role-Based Access Control (RBAC) Framework for Data Governance
Episode 47: Data Governance at Scale

Mumbai office की security की तरह multi-layered access control system 
जो ensure करता है कि right person को right data का right access मिले।

Author: Hindi Podcast Series
Context: Enterprise-grade access control for sensitive data
"""

import pandas as pd
import sqlite3
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import uuid
import logging
import hashlib
from pathlib import Path
import jwt
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AccessLevel(Enum):
    """Data access levels"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    AUDIT = "audit"

class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class RequestStatus(Enum):
    """Access request status"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class Role:
    """Role definition"""
    role_id: str
    role_name: str
    description: str
    department: str
    max_data_classification: DataClassification
    allowed_access_levels: List[AccessLevel]
    time_restrictions: Optional[Dict[str, Any]]  # Working hours, days etc.
    ip_restrictions: Optional[List[str]]
    created_at: datetime
    is_active: bool

@dataclass
class Permission:
    """Permission definition"""
    permission_id: str
    resource_pattern: str  # Database, table, column pattern
    data_classification: DataClassification
    access_levels: List[AccessLevel]
    conditions: Optional[Dict[str, Any]]  # Additional conditions
    created_at: datetime
    expires_at: Optional[datetime]

@dataclass
class User:
    """User definition"""
    user_id: str
    username: str
    email: str
    full_name: str
    employee_id: str
    department: str
    manager_id: Optional[str]
    roles: List[str]  # List of role IDs
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

@dataclass
class AccessRequest:
    """Access request"""
    request_id: str
    user_id: str
    resource: str
    access_level: AccessLevel
    justification: str
    requested_by: str
    requested_at: datetime
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    status: RequestStatus
    expiry_date: Optional[datetime]
    emergency_access: bool

@dataclass
class AccessLog:
    """Access log entry"""
    log_id: str
    user_id: str
    resource: str
    access_level: AccessLevel
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    reason: Optional[str]
    data_accessed: Optional[Dict[str, Any]]

class AccessControlFramework:
    """
    Comprehensive Role-Based Access Control (RBAC) framework
    
    Features:
    - Multi-level role hierarchy
    - Fine-grained permissions
    - Time-based access controls
    - IP-based restrictions
    - Emergency access procedures
    - Comprehensive audit logging
    - Dynamic access reviews
    - Compliance reporting
    """
    
    def __init__(self, db_path: str = "access_control.db", 
                 secret_key: str = "your-secret-key"):
        self.db_path = db_path
        self.secret_key = secret_key
        self.init_database()
        
        # Indian business hours (9 AM to 6 PM IST)
        self.business_hours = {
            'start_time': '09:00',
            'end_time': '18:00',
            'timezone': 'Asia/Kolkata'
        }
        
        # Common IP ranges for Indian offices
        self.office_ip_ranges = [
            '192.168.1.0/24',  # Mumbai office
            '192.168.2.0/24',  # Delhi office
            '192.168.3.0/24',  # Bangalore office
            '10.0.0.0/8'       # Corporate VPN
        ]
        
        logger.info("Access Control Framework initialized")
    
    def init_database(self):
        """Initialize access control database"""
        self.conn = sqlite3.connect(self.db_path)
        
        # Users table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                employee_id TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                manager_id TEXT,
                roles TEXT,  -- JSON array of role IDs
                is_active BOOLEAN DEFAULT 1,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (manager_id) REFERENCES users (user_id)
            )
        ''')
        
        # Roles table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role_id TEXT PRIMARY KEY,
                role_name TEXT UNIQUE NOT NULL,
                description TEXT,
                department TEXT,
                max_data_classification TEXT NOT NULL,
                allowed_access_levels TEXT NOT NULL,  -- JSON array
                time_restrictions TEXT,  -- JSON object
                ip_restrictions TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Permissions table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id TEXT PRIMARY KEY,
                resource_pattern TEXT NOT NULL,
                data_classification TEXT NOT NULL,
                access_levels TEXT NOT NULL,  -- JSON array
                conditions TEXT,  -- JSON object
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        
        # Role-Permission mapping
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS role_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id TEXT NOT NULL,
                permission_id TEXT NOT NULL,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                granted_by TEXT,
                FOREIGN KEY (role_id) REFERENCES roles (role_id),
                FOREIGN KEY (permission_id) REFERENCES permissions (permission_id),
                UNIQUE (role_id, permission_id)
            )
        ''')
        
        # Access requests table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS access_requests (
                request_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resource TEXT NOT NULL,
                access_level TEXT NOT NULL,
                justification TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                requested_at TIMESTAMP NOT NULL,
                approved_by TEXT,
                approved_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                expiry_date TIMESTAMP,
                emergency_access BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Access logs table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                log_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resource TEXT NOT NULL,
                access_level TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                success BOOLEAN NOT NULL,
                reason TEXT,
                data_accessed TEXT,  -- JSON object
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Create indexes for better performance
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_users_department ON users(department)',
            'CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)',
            'CREATE INDEX IF NOT EXISTS idx_access_logs_user ON access_logs(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp)',
            'CREATE INDEX IF NOT EXISTS idx_access_requests_status ON access_requests(status)',
            'CREATE INDEX IF NOT EXISTS idx_permissions_classification ON permissions(data_classification)'
        ]
        
        for index_sql in indexes:
            self.conn.execute(index_sql)
        
        self.conn.commit()
    
    def create_user(self, user: User) -> str:
        """Create a new user"""
        self.conn.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, email, full_name, employee_id, department, 
             manager_id, roles, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.user_id,
            user.username,
            user.email,
            user.full_name,
            user.employee_id,
            user.department,
            user.manager_id,
            json.dumps(user.roles),
            user.is_active,
            user.created_at
        ))
        
        self.conn.commit()
        logger.info(f"Created user: {user.username}")
        
        return user.user_id
    
    def create_role(self, role: Role) -> str:
        """Create a new role"""
        self.conn.execute('''
            INSERT OR REPLACE INTO roles 
            (role_id, role_name, description, department, max_data_classification,
             allowed_access_levels, time_restrictions, ip_restrictions, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            role.role_id,
            role.role_name,
            role.description,
            role.department,
            role.max_data_classification.value,
            json.dumps([level.value for level in role.allowed_access_levels]),
            json.dumps(role.time_restrictions) if role.time_restrictions else None,
            json.dumps(role.ip_restrictions) if role.ip_restrictions else None,
            role.created_at,
            role.is_active
        ))
        
        self.conn.commit()
        logger.info(f"Created role: {role.role_name}")
        
        return role.role_id
    
    def create_permission(self, permission: Permission) -> str:
        """Create a new permission"""
        self.conn.execute('''
            INSERT OR REPLACE INTO permissions 
            (permission_id, resource_pattern, data_classification, access_levels,
             conditions, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            permission.permission_id,
            permission.resource_pattern,
            permission.data_classification.value,
            json.dumps([level.value for level in permission.access_levels]),
            json.dumps(permission.conditions) if permission.conditions else None,
            permission.created_at,
            permission.expires_at
        ))
        
        self.conn.commit()
        logger.info(f"Created permission for resource: {permission.resource_pattern}")
        
        return permission.permission_id
    
    def assign_permission_to_role(self, role_id: str, permission_id: str, 
                                 granted_by: str) -> bool:
        """Assign a permission to a role"""
        try:
            self.conn.execute('''
                INSERT INTO role_permissions (role_id, permission_id, granted_by)
                VALUES (?, ?, ?)
            ''', (role_id, permission_id, granted_by))
            
            self.conn.commit()
            logger.info(f"Assigned permission {permission_id} to role {role_id}")
            
            return True
        
        except sqlite3.IntegrityError:
            logger.warning(f"Permission {permission_id} already assigned to role {role_id}")
            return False
    
    def check_access(self, user_id: str, resource: str, access_level: AccessLevel,
                    ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Check if user has access to resource"""
        
        # Get user details
        user = self._get_user(user_id)
        if not user or not user['is_active']:
            self._log_access(user_id, resource, access_level, False, 
                           "User not found or inactive", ip_address, user_agent)
            return {'allowed': False, 'reason': 'User not found or inactive'}
        
        # Get user roles
        user_roles = json.loads(user['roles']) if user['roles'] else []
        
        # Check each role for permissions
        for role_id in user_roles:
            role = self._get_role(role_id)
            if not role or not role['is_active']:
                continue
            
            # Check role-level access restrictions
            role_check = self._check_role_restrictions(role, access_level, ip_address)
            if not role_check['allowed']:
                continue
            
            # Check permissions for this role
            permissions = self._get_role_permissions(role_id)
            
            for permission in permissions:
                if self._resource_matches_pattern(resource, permission['resource_pattern']):
                    # Check if access level is allowed
                    allowed_levels = json.loads(permission['access_levels'])
                    if access_level.value in allowed_levels:
                        # Check data classification level
                        max_classification = DataClassification(role['max_data_classification'])
                        resource_classification = DataClassification(permission['data_classification'])
                        
                        if self._can_access_classification(max_classification, resource_classification):
                            # Check additional conditions
                            if self._check_permission_conditions(permission, user, resource):
                                self._log_access(user_id, resource, access_level, True, 
                                               "Access granted", ip_address, user_agent)
                                return {
                                    'allowed': True,
                                    'role': role['role_name'],
                                    'permission': permission['permission_id']
                                }
        
        # Access denied
        self._log_access(user_id, resource, access_level, False, 
                        "No matching permissions found", ip_address, user_agent)
        return {'allowed': False, 'reason': 'No matching permissions found'}
    
    def _get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        cursor = self.conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        
        return None
    
    def _get_role(self, role_id: str) -> Optional[Dict]:
        """Get role by ID"""
        cursor = self.conn.execute('SELECT * FROM roles WHERE role_id = ?', (role_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        
        return None
    
    def _get_role_permissions(self, role_id: str) -> List[Dict]:
        """Get all permissions for a role"""
        cursor = self.conn.execute('''
            SELECT p.* FROM permissions p
            JOIN role_permissions rp ON p.permission_id = rp.permission_id
            WHERE rp.role_id = ? AND (p.expires_at IS NULL OR p.expires_at > ?)
        ''', (role_id, datetime.now()))
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    
    def _check_role_restrictions(self, role: Dict, access_level: AccessLevel, 
                                ip_address: str = None) -> Dict[str, Any]:
        """Check role-level restrictions"""
        
        # Check allowed access levels
        allowed_levels = json.loads(role['allowed_access_levels'])
        if access_level.value not in allowed_levels:
            return {'allowed': False, 'reason': f'Access level {access_level.value} not allowed for role'}
        
        # Check time restrictions
        if role['time_restrictions']:
            time_restrictions = json.loads(role['time_restrictions'])
            if not self._check_time_restrictions(time_restrictions):
                return {'allowed': False, 'reason': 'Access outside allowed time window'}
        
        # Check IP restrictions
        if role['ip_restrictions'] and ip_address:
            ip_restrictions = json.loads(role['ip_restrictions'])
            if not self._check_ip_restrictions(ip_address, ip_restrictions):
                return {'allowed': False, 'reason': 'Access from unauthorized IP address'}
        
        return {'allowed': True}
    
    def _resource_matches_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches permission pattern"""
        # Simple pattern matching - in production, use more sophisticated matching
        if pattern == '*':
            return True
        
        if pattern.endswith('*'):
            return resource.startswith(pattern[:-1])
        
        return resource == pattern
    
    def _can_access_classification(self, user_max: DataClassification, 
                                  resource_classification: DataClassification) -> bool:
        """Check if user can access resource based on classification levels"""
        classification_hierarchy = {
            DataClassification.PUBLIC: 0,
            DataClassification.INTERNAL: 1,
            DataClassification.CONFIDENTIAL: 2,
            DataClassification.RESTRICTED: 3,
            DataClassification.TOP_SECRET: 4
        }
        
        user_level = classification_hierarchy[user_max]
        resource_level = classification_hierarchy[resource_classification]
        
        return user_level >= resource_level
    
    def _check_permission_conditions(self, permission: Dict, user: Dict, resource: str) -> bool:
        """Check additional permission conditions"""
        if not permission['conditions']:
            return True
        
        conditions = json.loads(permission['conditions'])
        
        # Check department restriction
        if 'department' in conditions:
            allowed_departments = conditions['department']
            if isinstance(allowed_departments, str):
                allowed_departments = [allowed_departments]
            
            if user['department'] not in allowed_departments:
                return False
        
        # Check time-based conditions
        if 'valid_hours' in conditions:
            valid_hours = conditions['valid_hours']
            current_hour = datetime.now().hour
            
            if not (valid_hours['start'] <= current_hour <= valid_hours['end']):
                return False
        
        return True
    
    def _check_time_restrictions(self, time_restrictions: Dict) -> bool:
        """Check time-based access restrictions"""
        current_time = datetime.now()
        
        # Check business hours
        if 'business_hours_only' in time_restrictions and time_restrictions['business_hours_only']:
            current_hour = current_time.hour
            if not (9 <= current_hour <= 18):  # 9 AM to 6 PM
                return False
        
        # Check allowed days
        if 'allowed_days' in time_restrictions:
            allowed_days = time_restrictions['allowed_days']
            current_day = current_time.strftime('%A').lower()
            if current_day not in [day.lower() for day in allowed_days]:
                return False
        
        return True
    
    def _check_ip_restrictions(self, ip_address: str, allowed_ips: List[str]) -> bool:
        """Check IP-based access restrictions"""
        # Simple IP checking - in production, use proper CIDR matching
        for allowed_ip in allowed_ips:
            if allowed_ip == '*' or ip_address.startswith(allowed_ip.split('/')[0][:7]):
                return True
        
        return False
    
    def _log_access(self, user_id: str, resource: str, access_level: AccessLevel,
                   success: bool, reason: str = None, ip_address: str = None,
                   user_agent: str = None, data_accessed: Dict = None):
        """Log access attempt"""
        log_id = str(uuid.uuid4())
        
        self.conn.execute('''
            INSERT INTO access_logs 
            (log_id, user_id, resource, access_level, timestamp, ip_address,
             user_agent, success, reason, data_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_id,
            user_id,
            resource,
            access_level.value,
            datetime.now(),
            ip_address,
            user_agent,
            success,
            reason,
            json.dumps(data_accessed) if data_accessed else None
        ))
        
        self.conn.commit()
    
    def request_access(self, access_request: AccessRequest) -> str:
        """Submit an access request"""
        self.conn.execute('''
            INSERT INTO access_requests 
            (request_id, user_id, resource, access_level, justification,
             requested_by, requested_at, status, expiry_date, emergency_access)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            access_request.request_id,
            access_request.user_id,
            access_request.resource,
            access_request.access_level.value,
            access_request.justification,
            access_request.requested_by,
            access_request.requested_at,
            access_request.status.value,
            access_request.expiry_date,
            access_request.emergency_access
        ))
        
        self.conn.commit()
        logger.info(f"Access request submitted: {access_request.request_id}")
        
        # Auto-approve if emergency access and user has emergency role
        if access_request.emergency_access:
            self._handle_emergency_access(access_request)
        
        return access_request.request_id
    
    def approve_access_request(self, request_id: str, approver_id: str,
                             approved: bool, reason: str = None) -> bool:
        """Approve or deny an access request"""
        status = RequestStatus.APPROVED if approved else RequestStatus.DENIED
        
        self.conn.execute('''
            UPDATE access_requests 
            SET status = ?, approved_by = ?, approved_at = ?
            WHERE request_id = ?
        ''', (status.value, approver_id, datetime.now(), request_id))
        
        self.conn.commit()
        
        action = "approved" if approved else "denied"
        logger.info(f"Access request {request_id} {action} by {approver_id}")
        
        if approved:
            self._grant_temporary_access(request_id)
        
        return True
    
    def _handle_emergency_access(self, access_request: AccessRequest):
        """Handle emergency access requests"""
        # Check if user has emergency access role
        user = self._get_user(access_request.user_id)
        if user:
            user_roles = json.loads(user['roles']) if user['roles'] else []
            
            # Check if any role allows emergency access
            for role_id in user_roles:
                role = self._get_role(role_id)
                if role and 'emergency_access' in role.get('description', '').lower():
                    # Auto-approve emergency access with short expiry
                    self.conn.execute('''
                        UPDATE access_requests 
                        SET status = 'approved', approved_by = 'system', 
                            approved_at = ?, expiry_date = ?
                        WHERE request_id = ?
                    ''', (
                        datetime.now(),
                        datetime.now() + timedelta(hours=4),  # 4 hour emergency access
                        access_request.request_id
                    ))
                    
                    self.conn.commit()
                    logger.info(f"Emergency access auto-approved: {access_request.request_id}")
                    break
    
    def _grant_temporary_access(self, request_id: str):
        """Grant temporary access based on approved request"""
        # This would typically create temporary permissions
        # For demo purposes, we just log it
        logger.info(f"Temporary access granted for request: {request_id}")
    
    def generate_access_report(self, user_id: str = None, 
                             date_from: datetime = None,
                             date_to: datetime = None) -> Dict[str, Any]:
        """Generate comprehensive access report"""
        
        # Build query conditions
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if date_from:
            conditions.append("timestamp >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("timestamp <= ?")
            params.append(date_to)
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Access statistics
        cursor = self.conn.execute(f'''
            SELECT 
                COUNT(*) as total_attempts,
                COUNT(CASE WHEN success = 1 THEN 1 END) as successful_attempts,
                COUNT(CASE WHEN success = 0 THEN 1 END) as failed_attempts,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(DISTINCT resource) as unique_resources
            FROM access_logs {where_clause}
        ''', params)
        
        access_stats = cursor.fetchone()
        
        # Most accessed resources
        cursor = self.conn.execute(f'''
            SELECT resource, COUNT(*) as access_count
            FROM access_logs {where_clause}
            GROUP BY resource
            ORDER BY access_count DESC
            LIMIT 10
        ''', params)
        
        top_resources = [{'resource': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Failed access attempts
        cursor = self.conn.execute(f'''
            SELECT user_id, resource, reason, COUNT(*) as failure_count
            FROM access_logs 
            {where_clause} {'AND' if where_clause else 'WHERE'} success = 0
            GROUP BY user_id, resource, reason
            ORDER BY failure_count DESC
            LIMIT 10
        ''', params)
        
        failed_attempts = []
        for row in cursor.fetchall():
            failed_attempts.append({
                'user_id': row[0],
                'resource': row[1],
                'reason': row[2],
                'count': row[3]
            })
        
        # Pending access requests
        cursor = self.conn.execute("SELECT COUNT(*) FROM access_requests WHERE status = 'pending'")
        pending_requests = cursor.fetchone()[0]
        
        return {
            'report_generated_at': datetime.now().isoformat(),
            'report_period': {
                'from': date_from.isoformat() if date_from else None,
                'to': date_to.isoformat() if date_to else None
            },
            'access_statistics': {
                'total_attempts': access_stats[0],
                'successful_attempts': access_stats[1],
                'failed_attempts': access_stats[2],
                'success_rate': (access_stats[1] / max(access_stats[0], 1)) * 100,
                'unique_users': access_stats[3],
                'unique_resources': access_stats[4]
            },
            'top_accessed_resources': top_resources,
            'failed_access_attempts': failed_attempts,
            'pending_requests': pending_requests,
            'security_alerts': self._generate_security_alerts(failed_attempts)
        }
    
    def _generate_security_alerts(self, failed_attempts: List[Dict]) -> List[str]:
        """Generate security alerts based on access patterns"""
        alerts = []
        
        # Check for repeated failures
        for attempt in failed_attempts:
            if attempt['count'] > 5:
                alerts.append(f"🚨 HIGH: User {attempt['user_id']} has {attempt['count']} failed attempts for {attempt['resource']}")
        
        # Check for suspicious patterns
        cursor = self.conn.execute('''
            SELECT user_id, COUNT(DISTINCT ip_address) as ip_count
            FROM access_logs
            WHERE timestamp > ?
            GROUP BY user_id
            HAVING ip_count > 3
        ''', (datetime.now() - timedelta(days=1),))
        
        for row in cursor.fetchall():
            alerts.append(f"⚠️ MEDIUM: User {row[0]} accessed from {row[1]} different IP addresses in last 24 hours")
        
        return alerts
    
    def review_user_access(self, user_id: str) -> Dict[str, Any]:
        """Comprehensive user access review"""
        user = self._get_user(user_id)
        if not user:
            return {'error': 'User not found'}
        
        # Get user roles and permissions
        user_roles = json.loads(user['roles']) if user['roles'] else []
        
        role_details = []
        for role_id in user_roles:
            role = self._get_role(role_id)
            if role:
                permissions = self._get_role_permissions(role_id)
                role_details.append({
                    'role': role,
                    'permissions_count': len(permissions),
                    'permissions': permissions
                })
        
        # Recent access activity
        cursor = self.conn.execute('''
            SELECT resource, access_level, success, timestamp
            FROM access_logs
            WHERE user_id = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (user_id, datetime.now() - timedelta(days=30)))
        
        recent_activity = []
        for row in cursor.fetchall():
            recent_activity.append({
                'resource': row[0],
                'access_level': row[1],
                'success': bool(row[2]),
                'timestamp': row[3]
            })
        
        # Access requests
        cursor = self.conn.execute('''
            SELECT request_id, resource, access_level, status, requested_at
            FROM access_requests
            WHERE user_id = ?
            ORDER BY requested_at DESC
            LIMIT 10
        ''', (user_id,))
        
        access_requests = []
        for row in cursor.fetchall():
            access_requests.append({
                'request_id': row[0],
                'resource': row[1],
                'access_level': row[2],
                'status': row[3],
                'requested_at': row[4]
            })
        
        return {
            'user_details': user,
            'roles_and_permissions': role_details,
            'recent_activity': recent_activity,
            'access_requests': access_requests,
            'risk_assessment': self._assess_user_risk(user_id, recent_activity)
        }
    
    def _assess_user_risk(self, user_id: str, recent_activity: List[Dict]) -> Dict[str, Any]:
        """Assess risk level for a user"""
        risk_score = 0
        risk_factors = []
        
        # Check failed attempts
        failed_count = sum(1 for activity in recent_activity if not activity['success'])
        if failed_count > 5:
            risk_score += 20
            risk_factors.append(f"High number of failed access attempts: {failed_count}")
        
        # Check access pattern
        if len(recent_activity) > 50:  # Very active user
            risk_score += 10
            risk_factors.append("Very high access activity")
        
        # Check for weekend/night access
        weekend_access = 0
        for activity in recent_activity:
            access_time = datetime.fromisoformat(activity['timestamp'])
            if access_time.weekday() >= 5:  # Weekend
                weekend_access += 1
        
        if weekend_access > 10:
            risk_score += 15
            risk_factors.append(f"High weekend access: {weekend_access} attempts")
        
        # Determine risk level
        if risk_score >= 40:
            risk_level = "HIGH"
        elif risk_score >= 20:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors
        }

def setup_sample_rbac_system():
    """Set up sample RBAC system with Indian corporate structure"""
    framework = AccessControlFramework()
    
    # Create roles
    roles = [
        Role(
            role_id="data_analyst",
            role_name="Data Analyst",
            description="Analyze business data and generate reports",
            department="Analytics",
            max_data_classification=DataClassification.CONFIDENTIAL,
            allowed_access_levels=[AccessLevel.READ, AccessLevel.AUDIT],
            time_restrictions={"business_hours_only": True},
            ip_restrictions=None,
            created_at=datetime.now(),
            is_active=True
        ),
        Role(
            role_id="data_engineer",
            role_name="Data Engineer",
            description="Develop and maintain data pipelines",
            department="Engineering",
            max_data_classification=DataClassification.CONFIDENTIAL,
            allowed_access_levels=[AccessLevel.READ, AccessLevel.WRITE],
            time_restrictions=None,
            ip_restrictions=None,
            created_at=datetime.now(),
            is_active=True
        ),
        Role(
            role_id="compliance_officer",
            role_name="Compliance Officer",
            description="Monitor compliance and data governance",
            department="Compliance",
            max_data_classification=DataClassification.RESTRICTED,
            allowed_access_levels=[AccessLevel.READ, AccessLevel.AUDIT, AccessLevel.ADMIN],
            time_restrictions=None,
            ip_restrictions=None,
            created_at=datetime.now(),
            is_active=True
        )
    ]
    
    for role in roles:
        framework.create_role(role)
    
    # Create permissions
    permissions = [
        Permission(
            permission_id="customer_data_read",
            resource_pattern="database.customers.*",
            data_classification=DataClassification.CONFIDENTIAL,
            access_levels=[AccessLevel.READ],
            conditions={"department": ["Analytics", "Customer Service"]},
            created_at=datetime.now(),
            expires_at=None
        ),
        Permission(
            permission_id="financial_data_read",
            resource_pattern="database.transactions.*",
            data_classification=DataClassification.RESTRICTED,
            access_levels=[AccessLevel.READ, AccessLevel.AUDIT],
            conditions={"department": ["Finance", "Compliance"]},
            created_at=datetime.now(),
            expires_at=None
        )
    ]
    
    for permission in permissions:
        framework.create_permission(permission)
    
    # Assign permissions to roles
    framework.assign_permission_to_role("data_analyst", "customer_data_read", "system")
    framework.assign_permission_to_role("compliance_officer", "financial_data_read", "system")
    
    # Create users
    users = [
        User(
            user_id="raj_analyst",
            username="raj.sharma",
            email="raj.sharma@company.com",
            full_name="राज शर्मा",
            employee_id="EMP001",
            department="Analytics",
            manager_id=None,
            roles=["data_analyst"],
            is_active=True,
            created_at=datetime.now()
        ),
        User(
            user_id="priya_compliance",
            username="priya.patel",
            email="priya.patel@company.com",
            full_name="प्रिया पटेल",
            employee_id="EMP002",
            department="Compliance",
            manager_id=None,
            roles=["compliance_officer"],
            is_active=True,
            created_at=datetime.now()
        )
    ]
    
    for user in users:
        framework.create_user(user)
    
    return framework

def main():
    """Main function demonstrating access control framework"""
    print("🔐 Starting Role-Based Access Control (RBAC) Framework Demo")
    print("=" * 70)
    
    # Set up sample system
    print("Setting up sample RBAC system...")
    framework = setup_sample_rbac_system()
    print("✅ RBAC system initialized with roles, permissions, and users")
    print()
    
    # Test access control
    print("🔍 Testing access control...")
    
    test_cases = [
        ("raj_analyst", "database.customers.profile", AccessLevel.READ, "192.168.1.10"),
        ("raj_analyst", "database.transactions.payments", AccessLevel.READ, "192.168.1.10"),
        ("priya_compliance", "database.transactions.payments", AccessLevel.AUDIT, "192.168.2.5"),
        ("raj_analyst", "database.customers.profile", AccessLevel.WRITE, "192.168.1.10"),
    ]
    
    for user_id, resource, access_level, ip in test_cases:
        result = framework.check_access(user_id, resource, access_level, ip, "Browser/1.0")
        
        status = "✅ ALLOWED" if result['allowed'] else "❌ DENIED"
        print(f"{status} - User: {user_id}")
        print(f"         Resource: {resource}")
        print(f"         Access Level: {access_level.value}")
        print(f"         Reason: {result.get('reason', 'Permission granted')}")
        print()
    
    # Test access request
    print("📝 Testing access request workflow...")
    
    access_request = AccessRequest(
        request_id=str(uuid.uuid4()),
        user_id="raj_analyst",
        resource="database.salaries.*",
        access_level=AccessLevel.READ,
        justification="Need salary data for compensation analysis project",
        requested_by="raj_analyst",
        requested_at=datetime.now(),
        approved_by=None,
        approved_at=None,
        status=RequestStatus.PENDING,
        expiry_date=datetime.now() + timedelta(days=30),
        emergency_access=False
    )
    
    request_id = framework.request_access(access_request)
    print(f"Access request submitted: {request_id}")
    
    # Approve the request
    framework.approve_access_request(request_id, "priya_compliance", True, "Approved for analysis project")
    print(f"Access request approved by compliance officer")
    print()
    
    # Generate access report
    print("📊 Generating access report...")
    report = framework.generate_access_report(
        date_from=datetime.now() - timedelta(days=1)
    )
    
    print("Access Statistics:")
    stats = report['access_statistics']
    print(f"  Total Attempts: {stats['total_attempts']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Unique Users: {stats['unique_users']}")
    print(f"  Unique Resources: {stats['unique_resources']}")
    print()
    
    if report['failed_access_attempts']:
        print("Failed Access Attempts:")
        for attempt in report['failed_access_attempts'][:3]:
            print(f"  - User: {attempt['user_id']}, Resource: {attempt['resource']}, Count: {attempt['count']}")
        print()
    
    if report['security_alerts']:
        print("Security Alerts:")
        for alert in report['security_alerts']:
            print(f"  {alert}")
        print()
    
    # User access review
    print("👤 Conducting user access review...")
    review = framework.review_user_access("raj_analyst")
    
    print(f"User: {review['user_details']['full_name']}")
    print(f"Department: {review['user_details']['department']}")
    print(f"Roles: {len(review['roles_and_permissions'])}")
    
    for role_info in review['roles_and_permissions']:
        role = role_info['role']
        print(f"  - {role['role_name']}: {role_info['permissions_count']} permissions")
    
    risk = review['risk_assessment']
    print(f"Risk Level: {risk['risk_level']} (Score: {risk['risk_score']})")
    
    if risk['risk_factors']:
        print("Risk Factors:")
        for factor in risk['risk_factors']:
            print(f"  - {factor}")
    
    print("\n✅ RBAC Framework demo completed successfully!")

if __name__ == "__main__":
    main()