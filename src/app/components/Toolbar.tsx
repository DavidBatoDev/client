"use client";

import React from "react";

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
    <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-4">
        {/* File Menu */}
        <div className="flex items-center space-x-2">
          <button className="px-3 py-1 text-sm hover:bg-gray-100 rounded">
            File
          </button>
          <button className="px-3 py-1 text-sm hover:bg-gray-100 rounded-xl">
            Edit
          </button>
          <button className="px-3 py-1 text-sm hover:bg-gray-100 rounded">
            View
          </button>
          <button className="px-3 py-1 text-sm hover:bg-gray-100 rounded">
            Insert
          </button>
        </div>

        {/* Formatting Tools */}
        <div className="flex items-center space-x-1 border-l border-gray-200 pl-4">
          <button className="p-2 hover:bg-gray-100 rounded" title="Bold">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4h8a4 4 0 110 8H3V4zm0 10h9a5 5 0 110 10H3v-10z" />
            </svg>
          </button>
          <button className="p-2 hover:bg-gray-100 rounded" title="Italic">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8 1h6v2H8V1zm0 16h6v2H8v-2zM6 3l4 14h2L8 3H6z" />
            </svg>
          </button>
          <button className="p-2 hover:bg-gray-100 rounded" title="Underline">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M6 2v8a4 4 0 008 0V2h2v8a6 6 0 01-12 0V2h2zm-4 16h16v2H2v-2z" />
            </svg>
          </button>
        </div>

        {/* Font Size */}
        <div className="flex items-center space-x-2 border-l border-gray-200 pl-4">
          <select className="px-2 py-1 text-sm border border-gray-300 rounded">
            <option>Arial</option>
            <option>Times New Roman</option>
            <option>Calibri</option>
            <option>Helvetica</option>
          </select>
          <select className="px-2 py-1 text-sm border border-gray-300 rounded w-16">
            <option>11</option>
            <option>12</option>
            <option>14</option>
            <option>16</option>
            <option>18</option>
            <option>20</option>
            <option>24</option>
          </select>
        </div>
      </div>

      {/* Zoom Controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onZoomOut}
          className="p-1 hover:bg-gray-100 rounded"
          title="Zoom Out (Ctrl + -)"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
              clipRule="evenodd"
            />
          </svg>
        </button>

        <button
          onClick={onResetZoom}
          className="px-2 py-1 text-sm hover:bg-gray-100 rounded min-w-[60px]"
          title="Reset Zoom (Ctrl + 0)"
        >
          {zoom}%
        </button>

        <button
          onClick={onZoomIn}
          className="p-1 hover:bg-gray-100 rounded"
          title="Zoom In (Ctrl + +)"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  );
};
