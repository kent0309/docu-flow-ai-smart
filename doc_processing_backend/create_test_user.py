#!/usr/bin/env python
"""
Script to create test users for approval workflow testing
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doc_processing_project.settings')
django.setup()

from django.contrib.auth.models import User

def create_test_users():
    """Create test users for approval workflows"""
    
    # Create test users
    users_to_create = [
        {
            'username': 'test_manager',
            'email': 'manager@test.com',
            'first_name': 'Test',
            'last_name': 'Manager',
            'password': 'testpass123'
        },
        {
            'username': 'test_approver',
            'email': 'approver@test.com',
            'first_name': 'Test',
            'last_name': 'Approver',
            'password': 'testpass123'
        },
        {
            'username': 'admin',
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True
        }
    ]
    
    created_users = []
    
    for user_data in users_to_create:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"✅ User '{username}' already exists")
            created_users.append(User.objects.get(username=username))
        else:
            # Create new user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            # Set staff/superuser status if specified
            if user_data.get('is_staff'):
                user.is_staff = True
            if user_data.get('is_superuser'):
                user.is_superuser = True
                
            user.save()
            created_users.append(user)
            print(f"✅ Created user '{username}' with email '{user_data['email']}'")
    
    print(f"\n🎉 Total users created/verified: {len(created_users)}")
    print("📋 User list:")
    for user in created_users:
        status = "Admin" if user.is_superuser else "Manager" if user.is_staff else "User"
        print(f"   - {user.username} ({user.email}) - {status}")
    
    return created_users

if __name__ == "__main__":
    print("🚀 Creating test users for approval workflows...")
    create_test_users()
    print("✅ Done!") 