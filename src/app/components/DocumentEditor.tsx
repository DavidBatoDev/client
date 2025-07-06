"use client";

import React, { useState, useEffect, useRef } from "react";
import { Toolbar } from "./Toolbar";
import { PageContainer } from "./PageContainer";
import { StatusBar } from "./StatusBar";

export interface TableData {
  id: string;
  height: number;
}

export interface Page {
  id: string;
  tables: TableData[];
}

export const DocumentEditor: React.FC = () => {
  const [pages, setPages] = useState<Page[]>([
    {
      id: "1",
      tables: [
        {
          id: "table-default",
          height: 300,
        },
      ],
    },
  ]);
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [zoom, setZoom] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const editorRef = useRef<HTMLDivElement>(null);

  // Handle zoom with Ctrl+scroll
  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -10 : 10;
        setZoom((prev) => Math.max(25, Math.min(500, prev + delta)));
      }
    };

    const editorElement = editorRef.current;
    if (editorElement) {
      editorElement.addEventListener("wheel", handleWheel, { passive: false });
      return () => editorElement.removeEventListener("wheel", handleWheel);
    }
  }, []);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey) {
        switch (e.key) {
          case "=":
          case "+":
            e.preventDefault();
            setZoom((prev) => Math.min(500, prev + 10));
            break;
          case "-":
            e.preventDefault();
            setZoom((prev) => Math.max(25, prev - 10));
            break;
          case "0":
            e.preventDefault();
            setZoom(100);
            break;
        }
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  const addPage = () => {
    const newPage: Page = {
      id: Date.now().toString(),
      tables: [
        {
          id: `table-default-${Date.now()}`,
          height: 300,
        },
      ],
    };
    setPages((prev) => [...prev, newPage]);
    setCurrentPageIndex(pages.length);
  };

  const removePage = (pageId: string) => {
    if (pages.length <= 1) return;

    setPages((prev) => prev.filter((page) => page.id !== pageId));
    setCurrentPageIndex((prev) => Math.max(0, prev - 1));
  };

  const updatePageTables = (pageId: string, tables: TableData[]) => {
    setPages((prev) =>
      prev.map((page) => (page.id === pageId ? { ...page, tables } : page))
    );
  };

  const zoomIn = () => setZoom((prev) => Math.min(500, prev + 10));
  const zoomOut = () => setZoom((prev) => Math.max(25, prev - 10));
  const resetZoom = () => setZoom(100);

  const insertTable = (afterTableId?: string) => {
    const tableId = `table-${Date.now()}`;
    const newTable: TableData = {
      id: tableId,
      height: 300,
    };

    const currentPage = pages[currentPageIndex];
    if (afterTableId) {
      // Insert after the specified table
      const afterIndex = currentPage.tables.findIndex(
        (table) => table.id === afterTableId
      );
      if (afterIndex !== -1) {
        const newTables = [...currentPage.tables];
        newTables.splice(afterIndex + 1, 0, newTable);
        updatePageTables(currentPage.id, newTables);
        return;
      }
    }
    // If no table ID specified or table not found, append to end
    const newTables = [...currentPage.tables, newTable];
    updatePageTables(currentPage.id, newTables);
  };

  const deleteTable = (tableId: string) => {
    const currentPage = pages[currentPageIndex];
    const newTables = currentPage.tables.filter(
      (table) => table.id !== tableId
    );
    updatePageTables(currentPage.id, newTables);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Toolbar
        zoom={zoom}
        onZoomIn={zoomIn}
        onZoomOut={zoomOut}
        onResetZoom={resetZoom}
      />

      <div
        ref={editorRef}
        className="flex-1 overflow-auto bg-gray-100 p-4"
        style={{
          cursor: "default",
          userSelect: "none",
        }}
      >
        <div className="flex justify-center">
          <PageContainer
            pages={pages}
            zoom={zoom}
            currentPageIndex={currentPageIndex}
            onPageTablesChange={updatePageTables}
            onPageClick={setCurrentPageIndex}
            onAddTable={insertTable}
            onAddPage={addPage}
            onDeleteTable={deleteTable}
            onDeletePage={removePage}
          />
        </div>
      </div>

      <StatusBar
        pages={pages}
        currentPageIndex={currentPageIndex}
        zoom={zoom}
        onAddPage={addPage}
        onRemovePage={removePage}
        onPageSelect={setCurrentPageIndex}
      />
    </div>
  );
};
