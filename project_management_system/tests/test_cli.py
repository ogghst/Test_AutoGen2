import asyncio
import pytest
from unittest.mock import MagicMock

from main import main as cli_main

@pytest.mark.asyncio
async def test_cli_init_project_and_exit(monkeypatch):
    """Test that the CLI can initialize a project and then exit."""
    
    # Arrange
    mock_input = MagicMock(side_effect=['init_project Name: Test Project', 'exit'])
    monkeypatch.setattr('builtins.input', mock_input)
    
    mock_console_constructor = MagicMock()
    monkeypatch.setattr('autogen_agentchat.ui.Console', mock_console_constructor)
    
    # Act
    await cli_main()
    
    # Assert
    # Check that the console was called with the stream from the groupchat
    mock_console_constructor.assert_called_once()
    
    # Check that the input function was called
    assert mock_input.call_count == 2