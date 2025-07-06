// client/src/app/components/PageContainer.tsx
"use client";

import React, { useEffect } from "react";
import { Page, TableData } from "./DocumentEditor";
import { Table as TableIcon } from "lucide-react";
import { Table } from "./Table";

interface PageContainerProps {
  pages: Page[];
  zoom: number;
  currentPageIndex: number;
  selectedTableId: string | null;
  onPageTablesChange: (pageId: string, tables: TableData[]) => void;
  onPageClick: (pageIndex: number) => void;
  onAddTable: (afterTableId?: string) => void;
  onAddPage: () => void;
  onDeleteTable: (tableId: string) => void;
  onDeletePage: (pageId: string) => void;
  onTableSelect: (tableId: string) => void;
}

export const PageContainer: React.FC<PageContainerProps> = ({
  pages,
  zoom,
  currentPageIndex,
  selectedTableId,
  onPageTablesChange,
  onPageClick,
  onAddTable,
  onAddPage,
  onDeleteTable,
  onDeletePage,
  onTableSelect,
}) => {
  const scale = zoom / 100;

  // Add effect to check and delete pages without tables
  useEffect(() => {
    pages.forEach((page) => {
      if (page.tables.length === 0) {
        onDeletePage(page.id);
      }
    });
  }, [pages, onDeletePage]);

  // Letter size dimensions in pixels (8.5" x 11" at 96 DPI)
  const letterWidth = 816;
  const letterHeight = 1056;

  const scaledWidth = letterWidth * scale;
  const scaledHeight = letterHeight * scale;

  return (
    <div
      className={`flex flex-col items-center space-y-4 ${
        pages.length === 1 ? "single-page" : ""
      }`}
    >
      {pages.map((page, index) => (
        <React.Fragment key={page.id}>
          <div
            className={`relative bg-white shadow-lg border page-container ${
              index === currentPageIndex
                ? "border-blue-500 shadow-blue-200"
                : "border-gray-300"
            }`}
            style={{
              width: letterWidth,
              height: letterHeight,
              transform: `scale(${scale})`,
              transformOrigin: "top center",
            }}
            onClick={() => onPageClick(index)}
            data-page-id={page.id}
          >
            {/* Page Number */}
            <div className="absolute -top-6 left-0 text-xs text-gray-500">
              Page {index + 1}
            </div>

            {/* Page Content Area */}
            <div
              className="w-full h-full p-16 outline-none resize-none relative"
              style={{
                fontSize: `${12 * scale}px`,
                lineHeight: "1.6",
                fontFamily: "Arial, sans-serif",
                cursor: "text",
                userSelect: "text",
              }}
            >
              {/* Render Tables with Add Table buttons */}
              {page.tables.map((tableData, tableIndex) => (
                <React.Fragment key={tableData.id}>
                  <Table
                    id={tableData.id}
                    initialHeight={tableData.height}
                    isSelected={selectedTableId === tableData.id}
                    onDelete={onDeleteTable}
                    onSelect={onTableSelect}
                    showDeleteButton={tableData.id !== "table-default"}
                    scale={scale}
                  />

                  {/* Add Table Button after each table (if under limit) */}
                  {page.tables.length < 2 && (
                    <div className="flex justify-center my-4">
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          onAddTable(tableData.id);
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 transition-colors text-sm"
                        style={{ pointerEvents: "auto" }}
                      >
                        <TableIcon size={16} />
                        <span>Add Table</span>
                      </button>
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>

            {/* Page Margins (Visual Guide) */}
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                border: `1px dashed rgba(0, 0, 0, 0.1)`,
                margin: `${64 * scale}px`,
              }}
            />

            {/* Ruler Lines (Optional) */}
            {zoom > 75 && (
              <div className="absolute inset-0 pointer-events-none">
                {/* Horizontal lines */}
                {Array.from({ length: 25 }, (_, i) => (
                  <div
                    key={`h-${i}`}
                    className="absolute w-full border-t border-gray-100"
                    style={{
                      top: `${(i + 1) * 40 * scale}px`,
                      opacity: 0.3,
                    }}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Add Page Button - appears after each page except the last */}
          {index < pages.length - 1 && (
            <div className="flex justify-center py-4">
              <button
                onClick={onAddPage}
                className="flex items-center space-x-2 px-6 py-3 bg-green-500 text-white rounded-full shadow-lg hover:bg-green-600 transition-colors text-sm opacity-70 hover:opacity-100"
                title="Add Page"
              >
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Add Page</span>
              </button>
            </div>
          )}
        </React.Fragment>
      ))}

      {/* Add Page Button at the end */}
      <div className="flex justify-center py-4">
        <button
          onClick={onAddPage}
          className="flex items-center space-x-2 px-6 py-3 bg-green-500 text-white rounded-full shadow-lg hover:bg-green-600 transition-colors text-sm opacity-70 hover:opacity-100"
          title="Add Page"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
              clipRule="evenodd"
            />
          </svg>
          <span>Add Page</span>
        </button>
      </div>
    </div>
  );
};
