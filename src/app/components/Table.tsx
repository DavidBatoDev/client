// client/src/app/components/Table.tsx
"use client";

import React, { useState, useRef, useEffect } from "react";
import { X } from "lucide-react";
import { TableToolbar } from "./TableToolbar";

interface TableProps {
  id: string;
  initialHeight?: number;
  isSelected?: boolean;
  onDelete?: (id: string) => void;
  onSelect?: (id: string) => void;
  showDeleteButton?: boolean;
  scale?: number;
}

export const Table: React.FC<TableProps> = ({
  id,
  initialHeight = 300,
  isSelected = false,
  onDelete,
  onSelect,
  showDeleteButton = true,
  scale = 1,
}) => {
  const [height, setHeight] = useState(initialHeight);
  const [isResizing, setIsResizing] = useState(false);
  const [showResizeHandle, setShowResizeHandle] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const startHeight = useRef(0);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true);
    startY.current = e.clientY;
    startHeight.current = height;
    document.body.style.cursor = "ns-resize";
    document.body.style.userSelect = "none";
  };

  const handleTableClick = (e: React.MouseEvent) => {
    if (onSelect) {
      onSelect(id);
    }
  };

  const handleCellClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onSelect && !isSelected) {
      onSelect(id);
    }
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;

      const deltaY = e.clientY - startY.current;
      const newHeight = Math.max(150, startHeight.current + deltaY);
      setHeight(newHeight);
    };

    const handleMouseUp = () => {
      if (isResizing) {
        setIsResizing(false);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      }
    };

    if (isResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing]);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete && id !== "table-default") {
      onDelete(id);
    }
  };

  return (
    <>
      <div
        ref={tableRef}
        className={`table-container relative my-5 ${
          isSelected ? "ring-2 ring-blue-500 ring-opacity-50" : ""
        }`}
        style={{ width: "100%" }}
        onMouseEnter={() => setShowResizeHandle(true)}
        onMouseLeave={() => !isResizing && setShowResizeHandle(false)}
        onClick={handleTableClick}
        data-table-id={id}
      >
        {/* Delete Button */}
        {showDeleteButton && id !== "table-default" && (
          <button
            onClick={handleDelete}
            className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors z-10 flex items-center justify-center"
            style={{ display: showResizeHandle ? "flex" : "none" }}
          >
            <X size={12} />
          </button>
        )}

        {/* Table Toolbar */}
        {isSelected && <TableToolbar position={{ x: 0, y: 0 }} tableId={id} />}

        {/* Table */}
        <div
          style={{
            width: "100%",
            border: "2px solid #000",
            display: "table",
            position: "relative",
            height: `${height}px`,
            cursor: "pointer",
          }}
          onClick={handleTableClick}
        >
          {/* Resize Handle */}
          <div
            className="resize-handle"
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              bottom: -3,
              height: 6,
              background: "#007bff",
              cursor: "ns-resize",
              opacity: showResizeHandle ? 1 : 0,
              transition: "opacity 0.2s",
            }}
            onMouseDown={handleMouseDown}
          />

          {/* Table Row */}
          <div
            style={{
              display: "table-row",
              height: `${height}px`,
            }}
          >
            {/* Left Cell */}
            <div
              contentEditable
              suppressContentEditableWarning={true}
              style={{
                display: "table-cell",
                border: "2px solid #000",
                padding: "10px",
                height: `${height}px`,
                verticalAlign: "top",
                width: "50%",
              }}
              className="outline-none"
              onClick={handleCellClick}
            >
              &nbsp;
            </div>

            {/* Right Cell */}
            <div
              contentEditable
              suppressContentEditableWarning={true}
              style={{
                display: "table-cell",
                border: "2px solid #000",
                padding: "10px",
                height: `${height}px`,
                verticalAlign: "top",
                width: "50%",
              }}
              className="outline-none"
              onClick={handleCellClick}
            >
              &nbsp;
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
