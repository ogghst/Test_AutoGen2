import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import { ThemeProvider } from './components/theme-provider';
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from './components/ui/resizable';
import { Menubar, MenubarMenu, MenubarTrigger } from './components/ui/menubar';
import DocumentSidebar from './components/DocumentSidebar';
import LogPanel from './components/LogPanel';

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <Router>
        <div className="flex flex-col h-screen bg-background text-foreground">
          <header className="flex h-10 items-center justify-between border-b px-4">
            <h1 className="text-lg font-semibold">Multi-Agent Project Management System</h1>
            <Menubar>
              <MenubarMenu>
                <MenubarTrigger>File</MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger>Edit</MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger>View</MenubarTrigger>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger>Help</MenubarTrigger>
              </MenubarMenu>
            </Menubar>
          </header>
          <div className="flex flex-grow">
            <ResizablePanelGroup direction="horizontal">
              <ResizablePanel defaultSize={25} minSize={20} collapsible={true}>
                <DocumentSidebar />
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={75}>
                <ResizablePanelGroup direction="vertical">
                  <ResizablePanel defaultSize={75}>
                    <Routes>
                      <Route path="/" element={<ChatPage />} />
                    </Routes>
                  </ResizablePanel>
                  <ResizableHandle withHandle />
                  <ResizablePanel defaultSize={25} minSize={10} collapsible={true}>
                    <LogPanel />
                  </ResizablePanel>
                </ResizablePanelGroup>
              </ResizablePanel>
            </ResizablePanelGroup>
          </div>
          <footer className="flex h-6 items-center justify-center border-t">
            <p className="text-xs text-muted-foreground">Status Bar</p>
          </footer>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
