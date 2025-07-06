"use client";

import React from "react";

interface RightColumnProps {
  height: number;
  hasImages: boolean;
  onMimic: () => void;
  onCellClick: (e: React.MouseEvent) => void;
  onDeselectImage: () => void;
}

export const RightColumn: React.FC<RightColumnProps> = ({
  height,
  hasImages,
  onMimic,
  onCellClick,
  onDeselectImage,
}) => {
  return (
    <div
      style={{
        display: "table-cell",
        border: "2px solid #000",
        padding: "10px",
        height: `${height}px`,
        verticalAlign: "top",
        width: "50%",
        position: "relative",
        overflow: "visible",
      }}
      className="outline-none"
      onClick={onCellClick}
    >
      {hasImages ? (
        <div className="flex flex-col items-center justify-center h-full">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onMimic();
            }}
            className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg transition-colors font-medium text-lg shadow-lg hover:shadow-xl"
          >
            Mimic
          </button>
        </div>
      ) : (
        <div
          contentEditable
          suppressContentEditableWarning={true}
          className="w-full h-full outline-none"
          onClick={(e) => {
            e.stopPropagation();
            onDeselectImage();
          }}
        >
          &nbsp;
        </div>
      )}
    </div>
  );
};
