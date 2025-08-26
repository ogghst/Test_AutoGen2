import React from 'react';

const LogPanel: React.FC = () => {
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Logs</h2>
      </div>
      <div className="flex-grow p-4">
        <p className="text-muted-foreground">Status logs will appear here.</p>
      </div>
    </div>
  );
};

export default LogPanel;
