# PowerSchool MCP Server - Example Usage

This document provides example queries and expected workflows for using the PowerSchool MCP server.

## Setup

Before using the MCP server, ensure you have configured the required environment variables:

```bash
export POWERSCHOOL_URL=https://your-school.powerschool.com
export POWERSCHOOL_CLIENT_ID=your_client_id
export POWERSCHOOL_CLIENT_SECRET=your_client_secret
export POWERSCHOOL_USERNAME=student_username
export POWERSCHOOL_PASSWORD=student_password
```

## Example Queries

Here are example queries you can use with AI assistants connected to this MCP server:

### Checking Server Configuration

**Query:** "Check if the PowerSchool server is properly configured"

**Tool Used:** `get_server_info`

**Expected Response:**
```json
{
  "server_name": "PowerSchool MCP Server",
  "version": "1.0.0",
  "environment": "production",
  "python_version": "3.13",
  "configuration": {
    "powerschool_url_set": true,
    "client_id_set": true,
    "client_secret_set": true,
    "username_set": true,
    "password_set": true
  },
  "configured": true
}
```

### Viewing Student Information

**Query:** "Show me my student information"

**Tool Used:** `get_student_info`

**Expected Response:** Student name, ID, grade level, school name, etc.

### Checking Current Grades

**Query:** "What are my current grades?"

**Tool Used:** `get_current_grades`

**Expected Response:** List of all courses with current grades, percentages, and letter grades.

### Viewing Assignments

**Query:** "Show me all my assignments"

**Tool Used:** `get_assignments`

**Expected Response:** Complete list of assignments across all courses.

**Query:** "Show me assignments for my math class (section ID 12345)"

**Tool Used:** `get_assignments` with parameter `section_id: 12345`

**Expected Response:** Assignments filtered to just the specified section.

### Checking Grade History

**Query:** "How have my grades changed over the last month?"

**Tool Used:** `get_grade_history` with date parameters

**Expected Response:** Historical grade data showing changes over time.

**Query:** "Show my grade history from September 1st to October 31st"

**Tool Used:** `get_grade_history` with parameters:
- `start_date: "2024-09-01"`
- `end_date: "2024-10-31"`

### Viewing Courses

**Query:** "What courses am I enrolled in?"

**Tool Used:** `get_courses`

**Expected Response:** List of all enrolled courses/sections with:
- Course names
- Teacher names
- Period/time
- Section IDs (useful for filtering assignments)

### Checking Attendance

**Query:** "Show me my attendance record"

**Tool Used:** `get_attendance`

**Expected Response:** Attendance records showing:
- Dates
- Status (present, absent, tardy, excused)
- Any notes or reasons

## Common Workflows

### Weekly Grade Check

1. Check current grades: `get_current_grades`
2. Review upcoming assignments: `get_assignments`
3. Check attendance: `get_attendance`

### Assignment Planning

1. Get list of courses: `get_courses` (to find section IDs)
2. Get assignments by course: `get_assignments(section_id=...)`
3. Review grade history: `get_grade_history` (to see trends)

### Progress Tracking

1. Get grade history for semester: `get_grade_history(start_date="2024-09-01")`
2. Compare with current grades: `get_current_grades`
3. Identify areas needing improvement

## Error Handling

The MCP tools return consistent error responses:

```json
{
  "success": false,
  "error": "Error message here"
}
```

Common errors:
- **Configuration errors**: Environment variables not set correctly
- **Authentication errors**: Invalid credentials or expired token
- **Connection errors**: PowerSchool server unreachable
- **Timeout errors**: Request took longer than 30 seconds

## Tips

1. **First-time setup**: Always run `get_server_info` first to verify configuration
2. **Finding section IDs**: Use `get_courses` to get section IDs for filtering assignments
3. **Date formats**: Use YYYY-MM-DD format for date parameters
4. **Rate limiting**: Be mindful of API rate limits from your PowerSchool server

## Integration Examples

### Claude Desktop

Add to your configuration file:

```json
{
  "mcpServers": {
    "powerschool": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Then ask Claude:
- "Use PowerSchool to check my grades"
- "Show my math assignments using PowerSchool"
- "What's my attendance record from PowerSchool?"

### API Testing with MCP Inspector

```bash
# Start the server
python src/server.py

# In another terminal
npx @modelcontextprotocol/inspector
```

Open http://localhost:3000 and test each tool interactively.

## Troubleshooting

### "PowerSchool configuration incomplete" error

**Problem:** Missing or incorrect environment variables

**Solution:** Verify all required variables are set:
```bash
echo $POWERSCHOOL_URL
echo $POWERSCHOOL_CLIENT_ID
# etc.
```

### "Failed to authenticate with PowerSchool" error

**Problem:** Invalid credentials or PowerSchool server not accessible

**Solution:**
1. Verify credentials are correct
2. Check PowerSchool URL is accessible
3. Verify OAuth2 is enabled on PowerSchool plugin
4. Check network connectivity

### "Request timed out" error

**Problem:** PowerSchool server taking longer than 30 seconds to respond

**Solution:**
1. Check PowerSchool server status
2. Verify network connection speed
3. Try again during off-peak hours

### Empty or unexpected responses

**Problem:** API endpoints may not be available or return different data

**Solution:**
1. Contact your school's PowerSchool administrator
2. Verify API endpoints are enabled
3. Check API permissions for student data access

## Support

For issues with:
- **This MCP server**: Check GitHub issues or create a new one
- **PowerSchool API**: Contact your school's IT department
- **MCP Protocol**: See [MCP Documentation](https://modelcontextprotocol.io/)
