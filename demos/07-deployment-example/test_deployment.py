#!/usr/bin/env python3
"""
Test script for the deployed Task Management MCP Server
Tests all available API endpoints to verify deployment functionality
"""

import requests
import json
import sys
from typing import Dict, Any
import time

BASE_URL = "https://deploy-example-openai-agents-sdk-mcp.onrender.com"

class DeploymentTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.created_task_id = None

    def test_endpoint(self, name: str, method: str, endpoint: str, data: Dict[Any, Any] = None, expected_status: int = 200):
        """Test a single endpoint and record results"""
        url = f"{self.base_url}{endpoint}"

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

            success = response.status_code == expected_status
            result = {
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "success": success,
                "response_size": len(response.content),
                "response_time": response.elapsed.total_seconds()
            }

            if success:
                try:
                    response_data = response.json()
                    result["response_preview"] = str(response_data)[:100] + "..." if len(str(response_data)) > 100 else str(response_data)

                    # Store task ID if we created one
                    if name == "Create Task" and "task_id" in str(response_data):
                        import re
                        match = re.search(r'"task_id":\s*"([^"]+)"', str(response_data))
                        if match:
                            self.created_task_id = match.group(1)

                except:
                    result["response_preview"] = "Non-JSON response"
            else:
                result["error"] = response.text[:200]

            self.test_results.append(result)
            return result

        except Exception as e:
            result = {
                "name": name,
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "error": str(e)
            }
            self.test_results.append(result)
            return result

    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Testing deployment endpoints...")
        print(f"Base URL: {self.base_url}")
        print("-" * 60)

        # Test health endpoints
        self.test_endpoint("Root Endpoint", "GET", "/")
        self.test_endpoint("Health Check", "GET", "/health")

        # Test task creation
        task_data = {
            "title": "Test Task",
            "description": "This is a test task created by the deployment test script",
            "priority": 4,
            "assignee": "test-user",
            "tags": ["test", "deployment"]
        }
        self.test_endpoint("Create Task", "POST", "/api/tasks/create", task_data)

        # Test task listing
        list_data = {"status_filter": None, "priority_filter": None}
        self.test_endpoint("List Tasks", "POST", "/api/tasks/list", list_data)

        # Test task search
        search_data = {"query": "test"}
        self.test_endpoint("Search Tasks", "POST", "/api/tasks/search", search_data)

        # Test MCP resources
        self.test_endpoint("All Tasks Resource", "GET", "/api/mcp/resources/all-tasks")
        self.test_endpoint("Pending Tasks Resource", "GET", "/api/mcp/resources/pending-tasks")
        self.test_endpoint("High Priority Resource", "GET", "/api/mcp/resources/high-priority")

        # Test MCP prompts
        self.test_endpoint("Task Summary Prompt", "GET", "/api/mcp/prompts/summary")
        self.test_endpoint("Daily Standup Prompt", "GET", "/api/mcp/prompts/standup")
        self.test_endpoint("Prioritization Prompt", "GET", "/api/mcp/prompts/prioritization")

        # Test agent chat
        chat_data = {"message": "show me all tasks"}
        self.test_endpoint("Agent Chat", "POST", "/api/agent/chat", chat_data)

        # Test task status update (if we have a task ID)
        if self.created_task_id:
            status_data = {"task_id": self.created_task_id, "new_status": "in_progress"}
            self.test_endpoint("Update Task Status", "PUT", "/api/tasks/status", status_data)

        # Test MCP info endpoints
        self.test_endpoint("MCP Tools Info", "GET", "/api/mcp/tools")
        self.test_endpoint("MCP Resources Info", "GET", "/api/mcp/resources")
        self.test_endpoint("MCP Prompts Info", "GET", "/api/mcp/prompts")

        # Test task deletion (if we have a task ID)
        if self.created_task_id:
            self.test_endpoint("Delete Task", "DELETE", f"/api/tasks/{self.created_task_id}")

    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['name']}: {result.get('error', 'Unknown error')}")

        print("\n✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result["success"]:
                time_str = f"{result.get('response_time', 0):.2f}s" if 'response_time' in result else "N/A"
                print(f"  • {result['name']} ({result['method']} {result['endpoint']}) - {time_str}")

        # Overall status
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! Deployment is working correctly.")
        elif passed_tests > failed_tests:
            print(f"\n⚠️  MOSTLY WORKING: {passed_tests}/{total_tests} tests passed.")
        else:
            print(f"\n🚨 DEPLOYMENT ISSUES: Only {passed_tests}/{total_tests} tests passed.")

        return failed_tests == 0

def main():
    """Main function to run deployment tests"""
    tester = DeploymentTester(BASE_URL)

    try:
        tester.run_all_tests()
        success = tester.print_results()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()