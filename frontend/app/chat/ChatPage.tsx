import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { ScrollArea } from '../components/ui/scroll-area';

// Define a type for the message structure
interface Message {
  id: string;
  text: string;
  type: 'user' | 'system' | 'thinking' | 'log' | 'agent';
}

// Define a type for the session response
interface SessionResponse {
  session_id: string;
}

const getAvatarForType = (type: Message['type']) => {
  switch (type) {
    case 'user':
      return 'U';
    case 'agent':
      return 'A';
    case 'system':
      return 'S';
    case 'thinking':
      return 'T';
    case 'log':
      return 'L';
    default:
      return '?';
  }
};

const getCardColorForType = (type: Message['type']) => {
  switch (type) {
    case 'user':
      return 'bg-primary text-primary-foreground';
    case 'agent':
      return 'bg-secondary text-secondary-foreground';
    case 'system':
      return 'bg-muted text-muted-foreground';
    case 'thinking':
      return 'bg-accent text-accent-foreground';
    case 'log':
      return 'bg-card text-card-foreground';
    default:
      return 'bg-card text-card-foreground';
  }
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const ws = useRef<WebSocket | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Create a session upon component mount
    const createSession = async () => {
      try {
        const response = await fetch('http://localhost:8001/api/session', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          throw new Error(`Failed to create session: ${response.status}`);
        }
        
        const sessionData: SessionResponse = await response.json();
        setSessionId(sessionData.session_id);
        setIsLoading(false);
      } catch (error) {
        console.error('Failed to create session:', error);
        setIsLoading(false);
      }
    };

    createSession();
  }, []);

  useEffect(() => {
    // Only connect to WebSocket after session is created
    if (!sessionId || isLoading) return;

    // Connect to the WebSocket server
    try {
      ws.current = new WebSocket(`ws://localhost:8001/ws/${sessionId}`);

      ws.current.onopen = () => {
        console.log('WebSocket connection established');
        setMessages(prev => [...prev, { id: uuidv4(), text: "Hello! How can I help you with your project today?", type: 'agent' }]);
      };

      ws.current.onmessage = (event) => {
        const newMessage: Message = {
          id: uuidv4(),
          text: event.data,
          type: 'agent',
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
  }, [sessionId, isLoading]);

  useEffect(() => {
    if (scrollAreaRef.current) {
        const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
        if (scrollContainer) {
            scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }
    }
  }, [messages]);

  const handleSend = () => {
    if (input.trim() !== '' && ws.current && ws.current.readyState === WebSocket.OPEN && !isLoading) {
      const newMessage: Message = {
        id: uuidv4(),
        text: input,
        type: 'user',
      };
      setMessages(prev => [...prev, newMessage]);
      ws.current.send(input);
      setInput('');
    }
  };

  // Show loading state while creating session
  if (isLoading) {
    return (
      <div className="flex flex-col h-full p-4 items-center justify-center">
        <div className="text-lg">Creating session...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full p-4">
      <ScrollArea className="flex-grow mb-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start gap-4 ${
                message.type === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.type !== 'user' && (
                <Avatar>
                  <AvatarFallback>{getAvatarForType(message.type)}</AvatarFallback>
                </Avatar>
              )}
              <Card className={`w-3/4 ${getCardColorForType(message.type)}`}>
                <CardContent className="p-4">
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </CardContent>
              </Card>
              {message.type === 'user' && (
                <Avatar>
                  <AvatarFallback>{getAvatarForType(message.type)}</AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>
      <div className="flex items-center gap-4">
        <Input
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSend();
            }
          }}
          disabled={isLoading}
        />
        <Button onClick={handleSend} disabled={isLoading}>Send</Button>
      </div>
    </div>
  );
};

export default ChatPage;
