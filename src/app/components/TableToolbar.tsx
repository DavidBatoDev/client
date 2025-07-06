// client/src/app/components/TableToolbar.tsx
"use client";

import React from "react";
import {
  MousePointer,
  Type,
  Square,
  Image,
  MoreHorizontal,
} from "lucide-react";

interface TableToolbarProps {
  position: { x: number; y: number };
  tableId: string;
}

export const TableToolbar: React.FC<TableToolbarProps> = ({
  position,
  tableId,
}) => {
  const handleToolClick = (tool: string) => {
    // TODO: Implement tool functionality
    console.log(`Tool clicked: ${tool} for table: ${tableId}`);
  };

  return (
    <div
      className="absolute bg-white rounded-lg shadow-lg border border-gray-200 p-2 z-[100]"
      style={{
        top: "-2rem",
        right: "-5rem",
      }}
    >
      <div className="flex items-center justify-center space-x-2">
        {/* Select/Cursor Tool */}
        <button
          onClick={() => handleToolClick("select")}
          className="w-8 h-8 flex items-center justify-center text-gray-700 hover:bg-gray-100 rounded transition-colors"
          title="Select"
        >
          <MousePointer size={16} />
        </button>

        {/* Text Tool */}
        <button
          onClick={() => handleToolClick("text")}
          className="w-8 h-8 flex items-center justify-center text-gray-700 hover:bg-gray-100 rounded transition-colors"
          title="Add Text"
        >
          <Type size={16} />
        </button>

        {/* Shapes Tool */}
        <button
          onClick={() => handleToolClick("shapes")}
          className="w-8 h-8 flex items-center justify-center text-gray-700 hover:bg-gray-100 rounded transition-colors"
          title="Add Shapes"
        >
          <Square size={16} />
        </button>

        {/* Image Tool */}
        <button
          onClick={() => handleToolClick("image")}
          className="w-8 h-8 flex items-center justify-center text-gray-700 hover:bg-gray-100 rounded transition-colors"
          title="Add Image"
        >
          <Image size={16} />
        </button>

        {/* More Tools */}
        <button
          onClick={() => handleToolClick("more")}
          className="w-8 h-8 flex items-center justify-center text-gray-700 hover:bg-gray-100 rounded transition-colors"
          title="More Tools"
        >
          <MoreHorizontal size={16} />
        </button>
      </div>
    </div>
  );
};
