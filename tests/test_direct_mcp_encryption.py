"""Direct test of MCP notes encryption without running server."""
from core.mcp.tool_registry import MCPToolRegistry

# Create registry instance
registry = MCPToolRegistry()

# Test save with encryption
result = registry._handle_notes({
    'action': 'save',
    'title': 'Direct Test - Encrypted Password',
    'input_content': 'password: w33fs3r2q35s4334@@#2ds',
    'encrypt_input': True
})

print("Save result:")
print(result)
print()

# Get the note ID from result
import re
match = re.search(r'ID: (\d+)', result)
if match:
    note_id = int(match.group(1))
    
    # Retrieve the note
    get_result = registry._handle_notes({
        'action': 'get',
        'note_id': note_id
    })
    
    print("Get result:")
    print(get_result)
    
    # Check database
    import sqlite3
    from core.data_directory import get_database_path
    conn = sqlite3.connect(get_database_path('notes.db'))
    row = conn.execute('SELECT Input FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()
    
    print()
    print("Database check:")
    print(f"Starts with ENC: {row[0].startswith('ENC:')}")
    print(f"First 50 chars: {row[0][:50]}")
