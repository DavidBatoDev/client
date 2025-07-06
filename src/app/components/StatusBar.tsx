// client/src/app/components/StatusBar.tsx
"use client";

import React from "react";
import { Page } from "./DocumentEditor";

interface StatusBarProps {
  pages: Page[];
  currentPageIndex: number;
  zoom: number;
  onAddPage: () => void;
  onRemovePage: (pageId: string) => void;
  onPageSelect: (pageIndex: number) => void;
}

export const StatusBar: React.FC<StatusBarProps> = ({
  pages,
  currentPageIndex,
  zoom,
  onAddPage,
  onRemovePage,
  onPageSelect,
}) => {
  return (
    <div className="bg-white border-t border-gray-200 px-4 py-2 flex items-center justify-between text-sm">
      {/* Left side - Page info */}
      <div className="flex items-center space-x-4">
        <span className="text-gray-600">
          Page {currentPageIndex + 1} of {pages.length}
        </span>
      </div>

      {/* Center - Page navigation */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onPageSelect(Math.max(0, currentPageIndex - 1))}
          disabled={currentPageIndex === 0}
          className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Previous Page"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
        </button>

        <div className="flex items-center space-x-1">
          {pages.map((_, index) => (
            <button
              key={index}
              onClick={() => onPageSelect(index)}
              className={`w-8 h-6 text-xs rounded ${
                index === currentPageIndex
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
              title={`Go to Page ${index + 1}`}
            >
              {index + 1}
            </button>
          ))}
        </div>

        <button
          onClick={() =>
            onPageSelect(Math.min(pages.length - 1, currentPageIndex + 1))
          }
          disabled={currentPageIndex === pages.length - 1}
          className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Next Page"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>

      {/* Right side - Zoom info and table count */}
      <div className="flex items-center space-x-4">
        <span className="text-gray-600">
          Tables:{" "}
          {pages.reduce((total, page) => {
            return total + page.tables.length;
          }, 0)}
        </span>

        <div className="flex items-center space-x-2">
          <span className="text-gray-600">Zoom:</span>
          <span className="font-medium">{zoom}%</span>
        </div>
      </div>
    </div>
  );
};
