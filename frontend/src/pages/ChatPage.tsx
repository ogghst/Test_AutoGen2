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
  const [sessionId] = useState<string>(uuidv4());
  const ws = useRef<WebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Connect to the WebSocket server
    ws.current = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);

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

    // Cleanup on component unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [sessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scroll_ref.current.scrollHeight;
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
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSend();
                }
              }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSend}
              sx={{ ml: 1 }}
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
