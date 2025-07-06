// client/src/app/components/Toolbar.tsx
"use client";

import React from "react";
import { ZoomIn, ZoomOut, RotateCcw } from "lucide-react";

interface ToolbarProps {
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  zoom,
  onZoomIn,
  onZoomOut,
  onResetZoom,
}) => {
  return (
    <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between">
      {/* Left side - Main tools */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Document Editor</span>
        </div>
      </div>

      {/* Right side - Zoom controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onZoomOut}
          className="p-2 hover:bg-gray-100 rounded-md transition-colors"
          title="Zoom Out"
        >
          <ZoomOut size={16} />
        </button>
        
        <button
          onClick={onResetZoom}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors"
          title="Reset Zoom"
        >
          {zoom}%
        </button>
        
        <button
          onClick={onZoomIn}
          className="p-2 hover:bg-gray-100 rounded-md transition-colors"
          title="Zoom In"
        >
          <ZoomIn size={16} />
        </button>
      </div>
    </div>
  );
};