# MCP Server Prompt Templates

These templates provide structured prompts for building different types of MCP servers using LLMs like Claude Code. Replace the `{placeholders}` with specific requirements and documentation.

## Template 1: Database/API Integration Server

```
I need you to build an MCP server that integrates with {DATABASE_TYPE/API_NAME}. Here are the requirements:

**Server Purpose:**
- Connect to {DATABASE_TYPE/API_NAME} at {CONNECTION_DETAILS}
- Provide read/write access to {SPECIFIC_TABLES/ENDPOINTS}
- Enable {SPECIFIC_USE_CASES}

**Required Tools:**
- {TOOL_NAME_1}: {TOOL_DESCRIPTION_1}
- {TOOL_NAME_2}: {TOOL_DESCRIPTION_2}
- {TOOL_NAME_3}: {TOOL_DESCRIPTION_3}

**Required Resources:**
- {RESOURCE_NAME_1}: {RESOURCE_DESCRIPTION_1}
- {RESOURCE_NAME_2}: {RESOURCE_DESCRIPTION_2}

**Documentation Context:**
{INSERT_MCP_SDK_DOCS}
{INSERT_DATABASE/API_SPECIFIC_DOCS}
{INSERT_AUTHENTICATION_REQUIREMENTS}

**Security Requirements:**
- {AUTHENTICATION_METHOD}
- {RATE_LIMITING_REQUIREMENTS}
- {DATA_VALIDATION_RULES}

**Testing Requirements:**
- Create a test client that demonstrates all functionality
- Include error handling for {SPECIFIC_ERROR_SCENARIOS}
- Validate all inputs and outputs

Please implement this step by step, starting with the basic connection and core tools, then adding resources and advanced features.
```

## Template 2: File System Management Server

```
Build an MCP server for advanced file system operations with the following specifications:

**Server Purpose:**
- Manage files and directories in {TARGET_DIRECTORY_PATH}
- Provide {FILE_OPERATION_TYPES} capabilities
- Support {FILE_FORMATS} with specialized handling

**Core Tools:**
- search_files: Search files by {SEARCH_CRITERIA}
- process_file: {FILE_PROCESSING_OPERATIONS}
- batch_operations: {BATCH_OPERATION_TYPES}
- file_analysis: {ANALYSIS_FEATURES}

**Resources to Expose:**
- file_metadata: Metadata for files matching {CRITERIA}
- directory_structure: Hierarchical view of {SCOPE}
- file_contents: Content access for {FILE_TYPES}

**Prompts to Include:**
- file_summary: Generate summaries for {FILE_TYPES}
- code_analysis: Analyze {PROGRAMMING_LANGUAGES}
- documentation_generator: Create docs for {DOCUMENTATION_TYPES}

**Documentation Context:**
{INSERT_MCP_SDK_DOCS}
{INSERT_FILE_SYSTEM_LIBRARIES_DOCS}
{INSERT_SECURITY_BEST_PRACTICES}

**Safety Requirements:**
- Restrict operations to {ALLOWED_PATHS}
- Prevent access to {RESTRICTED_PATTERNS}
- Validate all file paths and operations
- Log all file modifications

**Performance Considerations:**
- Handle large files efficiently
- Implement streaming for {LARGE_FILE_SCENARIOS}
- Cache {CACHEABLE_OPERATIONS}

Please start with basic file operations and gradually add advanced features like batch processing and analysis tools.
```

## Template 3: Development Workflow Server

```
Create an MCP server that enhances development workflows with the following capabilities:

**Server Purpose:**
- Integrate with {VERSION_CONTROL_SYSTEM} repositories
- Provide {CI_CD_PLATFORM} integration
- Support {DEVELOPMENT_TOOLS} automation

**Development Tools:**
- code_quality: Run {LINTING_TOOLS} and {TESTING_FRAMEWORKS}
- git_operations: {GIT_COMMANDS} with safety checks
- deploy_management: {DEPLOYMENT_OPERATIONS}
- project_analysis: {ANALYSIS_TYPES}

**Resources to Provide:**
- project_status: Current state of {PROJECT_COMPONENTS}
- test_results: Results from {TEST_SUITES}
- deployment_logs: Logs from {DEPLOYMENT_ENVIRONMENTS}
- code_metrics: Metrics for {METRIC_TYPES}

**Automation Prompts:**
- commit_message_generator: Generate messages for {COMMIT_TYPES}
- code_reviewer: Review {CODE_REVIEW_FOCUS_AREAS}
- documentation_updater: Update {DOCUMENTATION_TYPES}

**Integration Context:**
{INSERT_MCP_SDK_DOCS}
{INSERT_GIT_LIBRARY_DOCS}
{INSERT_CI_CD_API_DOCS}
{INSERT_DEVELOPMENT_TOOLS_DOCS}

**Workflow Requirements:**
- Support {BRANCHING_STRATEGY}
- Integrate with {ISSUE_TRACKING_SYSTEM}
- Handle {DEPLOYMENT_STRATEGIES}
- Monitor {MONITORING_METRICS}

**Security & Compliance:**
- Validate all repository operations
- Prevent destructive actions without confirmation
- Log all automated changes
- Respect {PERMISSION_LEVELS}

**Testing Strategy:**
- Mock external integrations for testing
- Create test repositories for validation
- Include rollback procedures for critical operations

Please implement this incrementally, starting with basic git operations, then adding CI/CD integration, and finally advanced workflow automation.
```

## Usage Instructions

1. **Choose the appropriate template** based on your MCP server needs
2. **Replace all {placeholders}** with your specific requirements
3. **Gather relevant documentation** for the {INSERT_DOCS} sections:
   - MCP Python SDK documentation
   - API documentation for external services
   - Security requirements and best practices
   - Library-specific documentation
4. **Provide the complete prompt** to Claude Code or another LLM
5. **Iterate and refine** based on initial implementation results

## Additional Tips

- Start with the simplest version and add complexity gradually
- Always include comprehensive error handling and input validation
- Test each component thoroughly before moving to the next
- Use the MCP Inspector (`mcp dev ./your_server.py`) for debugging
- Consider rate limiting and resource management for production use
- Document all tools, resources, and prompts clearly for end users