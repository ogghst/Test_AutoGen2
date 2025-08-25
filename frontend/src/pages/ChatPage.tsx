import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, Button, List, ListItem, Paper, Typography, Container, AppBar, Toolbar } from '@mui/material';
import { v4 as uuidv4 } from 'uuid';

// Define a type for the message structure
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const createNewSession = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/session', {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
      } else {
        console.error('Failed to create a new session');
      }
    } catch (error) {
      console.error('Error creating new session:', error);
    }
  };

  useEffect(() => {
    if (!sessionId) {
      return;
    }

    // Connect to the WebSocket server
    try {
      ws.current = new WebSocket(`ws://localhost:8001/ws/${sessionId}`);

      ws.current.onopen = () => {
        console.log('WebSocket connection established');
        setMessages(prev => [...prev, { id: uuidv4(), text: "Hello! How can I help you with your project today?", sender: 'agent' }]);
      };

      ws.current.onmessage = (event) => {
        const newMessage: Message = {
          id: uuidv4(),
          text: event.data,
          sender: 'agent',
        };
        setMessages(prev => [...prev, newMessage]);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.current.onclose = () => {
        console.log('WebSocket connection closed');
      };
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
    }

    // Cleanup on component unmount
    return () => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.close();
      }
    };
  }, [sessionId]);

    useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (input.trim() !== '' && ws.current && ws.current.readyState === WebSocket.OPEN) {
      const newMessage: Message = {
        id: uuidv4(),
        text: input,
        sender: 'user',
      };
      setMessages(prev => [...prev, newMessage]);
      ws.current.send(input);
      setInput('');
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ height: '80vh', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Multi-Agent Chat
            </Typography>
            {!sessionId && (
              <Button color="inherit" onClick={createNewSession}>
                New Session
              </Button>
            )}
          </Toolbar>
        </AppBar>
        <Box ref={scrollRef} sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          <List>
            {messages.map((message) => (
              <ListItem key={message.id} sx={{ justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start' }}>
                <Paper
                  elevation={1}
                  sx={{
                    p: 1.5,
                    bgcolor: message.sender === 'user' ? 'primary.main' : 'grey.300',
                    color: message.sender === 'user' ? 'primary.contrastText' : 'black',
                    borderRadius: message.sender === 'user' ? '20px 20px 5px 20px' : '20px 20px 20px 5px',
                    mb: 1,
                  }}
                >
                  <Typography variant="body1">{message.text}</Typography>
                </Paper>
              </ListItem>
            ))}
          </List>
        </Box>
        <Box sx={{ p: 2, borderTop: '1px solid #ddd' }}>
          <Box sx={{ display: 'flex' }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type a message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSend();
                }
              }}
              disabled={!sessionId}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSend}
              sx={{ ml: 1 }}
              disabled={!sessionId}
            >
              Send
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
};

export default ChatPage;
