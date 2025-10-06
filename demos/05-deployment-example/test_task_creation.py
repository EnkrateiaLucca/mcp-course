#!/usr/bin/env python3
"""
Test script for creating 3 tasks and verifying they are stored in the database
Shows detailed responses to demonstrate task creation and database storage
"""

import requests
import json
import sys
from typing import Dict, Any, List
import time

BASE_URL = "http://localhost:8000"

class TaskCreationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.created_tasks = []
        self.test_results = []

    def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[str, Any]:
        """Make HTTP request and return detailed response info"""
        url = f"{self.base_url}{endpoint}"
        
        print(f"\n🔄 Making {method} request to: {endpoint}")
        if data:
            print(f"📤 Request data: {json.dumps(data, indent=2)}")
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print(f"📊 Status Code: {response.status_code}")
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                print(f"📥 JSON Response:")
                print(json.dumps(response_data, indent=2))
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response_data,
                    "response_time": response.elapsed.total_seconds()
                }
            except json.JSONDecodeError:
                print(f"📥 Text Response: {response.text}")
                return {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "data": response.text,
                    "response_time": response.elapsed.total_seconds()
                }
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_task(self, title: str, description: str, priority: int, assignee: str, tags: List[str]) -> Dict[str, Any]:
        """Create a single task and return the result"""
        print(f"\n{'='*60}")
        print(f"📝 CREATING TASK: {title}")
        print(f"{'='*60}")
        
        task_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "assignee": assignee,
            "tags": tags
        }
        
        result = self.make_request("POST", "/api/tasks/create", task_data)
        
        if result["success"] and "data" in result and isinstance(result["data"], dict):
            # Check for task ID in the response (API uses "id" field)
            task_id = None
            if "task" in result["data"] and "id" in result["data"]["task"]:
                task_id = result["data"]["task"]["id"]
            elif "id" in result["data"]:
                task_id = result["data"]["id"]
            
            if task_id:
                self.created_tasks.append({
                    "task_id": task_id,
                    "title": title,
                    "priority": priority,
                    "assignee": assignee
                })
                print(f"✅ Task created successfully with ID: {task_id}")
            else:
                print(f"⚠️  Task creation response doesn't contain task ID")
        else:
            print(f"❌ Task creation failed")
            
        return result

    def list_all_tasks(self) -> Dict[str, Any]:
        """List all tasks to verify they exist in the database"""
        print(f"\n{'='*60}")
        print(f"📋 LISTING ALL TASKS")
        print(f"{'='*60}")
        
        list_data = {"status_filter": None, "priority_filter": None}
        result = self.make_request("POST", "/api/tasks/list", list_data)
        
        if result["success"] and "data" in result and isinstance(result["data"], dict):
            tasks = result["data"].get("tasks", [])
            print(f"📊 Found {len(tasks)} total tasks in database")
            
            # Check if our created tasks are in the list
            created_task_ids = [task["task_id"] for task in self.created_tasks]
            found_tasks = [task for task in tasks if task.get("id") in created_task_ids]
            print(f"✅ {len(found_tasks)} of our created tasks found in database")
            
            for task in found_tasks:
                print(f"  • {task.get('title', 'Unknown')} (ID: {task.get('id', 'Unknown')})")
        else:
            print(f"❌ Failed to list tasks")
            
        return result

    def search_tasks(self, query: str) -> Dict[str, Any]:
        """Search for tasks to verify they can be found"""
        print(f"\n{'='*60}")
        print(f"🔍 SEARCHING TASKS: '{query}'")
        print(f"{'='*60}")
        
        search_data = {"query": query}
        result = self.make_request("POST", "/api/tasks/search", search_data)
        
        if result["success"] and "data" in result and isinstance(result["data"], dict):
            tasks = result["data"].get("tasks", [])
            print(f"📊 Found {len(tasks)} tasks matching '{query}'")
            
            for task in tasks:
                print(f"  • {task.get('title', 'Unknown')} (ID: {task.get('id', 'Unknown')})")
        else:
            print(f"❌ Search failed")
            
        return result

    def get_task_details(self, task_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific task"""
        print(f"\n{'='*60}")
        print(f"🔍 GETTING TASK DETAILS: {task_id}")
        print(f"{'='*60}")
        
        result = self.make_request("GET", f"/api/tasks/{task_id}")
        
        if result["success"] and "data" in result:
            print(f"✅ Task details retrieved successfully")
        else:
            print(f"❌ Failed to get task details")
            
        return result

    def update_task_status(self, task_id: str, new_status: str) -> Dict[str, Any]:
        """Update the status of a task"""
        print(f"\n{'='*60}")
        print(f"🔄 UPDATING TASK STATUS: {task_id} -> {new_status}")
        print(f"{'='*60}")
        
        status_data = {"task_id": task_id, "new_status": new_status}
        result = self.make_request("PUT", "/api/tasks/status", status_data)
        
        if result["success"]:
            print(f"✅ Task status updated successfully")
        else:
            print(f"❌ Failed to update task status")
            
        return result

    def run_task_creation_tests(self):
        """Run the complete task creation and verification test suite"""
        print("🚀 Starting Task Creation and Database Verification Tests")
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Create 3 different tasks
        tasks_to_create = [
            {
                "title": "Database Integration Task",
                "description": "Implement database integration for the MCP server with proper error handling and connection pooling",
                "priority": 5,
                "assignee": "backend-dev",
                "tags": ["database", "backend", "high-priority"]
            },
            {
                "title": "API Documentation Update",
                "description": "Update API documentation to include all new MCP endpoints and provide examples for each",
                "priority": 3,
                "assignee": "tech-writer",
                "tags": ["documentation", "api", "maintenance"]
            },
            {
                "title": "Performance Optimization",
                "description": "Optimize database queries and add caching layer to improve response times",
                "priority": 4,
                "assignee": "senior-dev",
                "tags": ["performance", "optimization", "caching"]
            }
        ]
        
        # Create all tasks
        for i, task_info in enumerate(tasks_to_create, 1):
            print(f"\n🎯 Creating Task {i}/3")
            self.create_task(**task_info)
            time.sleep(1)  # Small delay between requests
        
        # Test 2: List all tasks to verify they're in the database
        print(f"\n🔍 VERIFICATION PHASE")
        self.list_all_tasks()
        
        # Test 3: Search for specific tasks
        self.search_tasks("database")
        self.search_tasks("API")
        self.search_tasks("performance")
        
        # Test 4: Get details for each created task
        for task in self.created_tasks:
            self.get_task_details(task["task_id"])
        
        # Test 5: Update status of one task
        if self.created_tasks:
            self.update_task_status(self.created_tasks[0]["task_id"], "in_progress")
        
        # Test 6: Final verification - list tasks again
        print(f"\n🔍 FINAL VERIFICATION")
        self.list_all_tasks()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        print(f"✅ Tasks Created: {len(self.created_tasks)}")
        for task in self.created_tasks:
            print(f"  • {task['title']} (ID: {task['task_id']})")
        
        print(f"\n🎯 Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(self.created_tasks) == 3:
            print(f"🎉 SUCCESS: All 3 tasks were created and should be stored in the database!")
        else:
            print(f"⚠️  WARNING: Only {len(self.created_tasks)} out of 3 tasks were created successfully")

def main():
    """Main function to run task creation tests"""
    tester = TaskCreationTester(BASE_URL)

    try:
        tester.run_task_creation_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
