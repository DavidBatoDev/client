// client/src/app/components/Table.tsx
"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { X, Upload, Image as ImageIcon } from "lucide-react";
import { useDropzone } from "react-dropzone";
import { TableToolbar } from "./TableToolbar";
import { RightColumn } from "./RightColumn";

interface TableProps {
  id: string;
  initialHeight?: number;
  isSelected?: boolean;
  onDelete?: (id: string) => void;
  onSelect?: (id: string) => void;
  showDeleteButton?: boolean;
  scale?: number;
  onHeightChange?: (tableId: string, height: number) => void;
}

export const Table: React.FC<TableProps> = ({
  id,
  initialHeight = 300,
  isSelected = false,
  onDelete,
  onSelect,
  showDeleteButton = true,
  scale = 1,
  onHeightChange,
}) => {
  const [height, setHeight] = useState(initialHeight);
  const [isResizing, setIsResizing] = useState(false);
  const [showResizeHandle, setShowResizeHandle] = useState(false);
  const [textFields, setTextFields] = useState<any[]>([]);
  const [shapes, setShapes] = useState<any[]>([]);
  const [leftColumnImages, setLeftColumnImages] = useState<
    Array<{
      id: string;
      src: string;
      width: number;
      height: number;
      x: number;
      y: number;
    }>
  >([]);
  const [isImageResizing, setIsImageResizing] = useState(false);
  const [resizingImageId, setResizingImageId] = useState<string | null>(null);
  const [resizeDirection, setResizeDirection] = useState<string>("");
  const [selectedImageId, setSelectedImageId] = useState<string | null>(null);
  const tableRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const startHeight = useRef(0);
  const startX = useRef(0);
  const startWidth = useRef(0);
  const startImageX = useRef(0);
  const startImageY = useRef(0);

  // Dropzone configuration
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      acceptedFiles.forEach((file) => {
        const reader = new FileReader();
        reader.onload = (event) => {
          const imageUrl = event.target?.result as string;

          // Calculate the Y position for the new image to avoid overlap
          let newY = 0;
          if (leftColumnImages.length > 0) {
            // Find the bottom of the last image and add spacing
            const lastImage = leftColumnImages[leftColumnImages.length - 1];
            newY = lastImage.y + lastImage.height + 20; // 20px spacing between images
          }

          const newImage = {
            id: `img-${Date.now()}-${Math.random()}`,
            src: imageUrl,
            width: 200,
            height: 200,
            x: 0,
            y: newY,
          };

          setLeftColumnImages((prev) => [...prev, newImage]);

          // Adjust table height to accommodate the new image
          const newTableHeight = Math.max(150, newY + 200 + 40); // image height + padding
          setHeight(newTableHeight);
        };
        reader.readAsDataURL(file);
      });
    },
    [leftColumnImages]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".gif", ".webp"],
    },
    multiple: true,
  });

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true);
    startY.current = e.clientY;
    startHeight.current = height;
    document.body.style.cursor = "ns-resize";
    document.body.style.userSelect = "none";
  };

  const handleImageMouseDown = (
    e: React.MouseEvent,
    imageId: string,
    direction: string
  ) => {
    e.stopPropagation();
    setIsImageResizing(true);
    setResizingImageId(imageId);
    setResizeDirection(direction);
    startX.current = e.clientX;
    startY.current = e.clientY;

    const image = leftColumnImages.find((img) => img.id === imageId);
    if (image) {
      startWidth.current = image.width;
      startHeight.current = image.height;
      startImageX.current = image.x;
      startImageY.current = image.y;
    }

    document.body.style.cursor = "ns-resize";
    document.body.style.userSelect = "none";
  };

  const handleTableClick = (e: React.MouseEvent) => {
    // Deselect the currently selected image when clicking on the table
    setSelectedImageId(null);
    if (onSelect) {
      onSelect(id);
    }
  };

  const handleCellClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    // Deselect the currently selected image when clicking elsewhere in the cell
    setSelectedImageId(null);
    if (onSelect && !isSelected) {
      onSelect(id);
    }
  };

  const handleImageClick = (e: React.MouseEvent, imageId: string) => {
    e.stopPropagation();
    setSelectedImageId(imageId);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizing) {
        const deltaY = e.clientY - startY.current;
        const newHeight = Math.max(150, startHeight.current + deltaY);
        setHeight(newHeight);
      }

      if (isImageResizing && resizingImageId) {
        const deltaX = e.clientX - startX.current;
        const deltaY = e.clientY - startY.current;

        setLeftColumnImages((prevImages) => {
          const updatedImages = prevImages.map((img) => {
            if (img.id === resizingImageId) {
              let newWidth = img.width;
              let newHeight = img.height;
              let newX = img.x;
              let newY = img.y;

              // Calculate cell boundaries based on actual cell width
              const cellPadding = 0; // 10px padding on each side
              const tableWidth = tableRef.current?.offsetWidth || 800; // Get actual table width
              const cellWidth = tableWidth * 0.5; // 50% of table width
              const maxImageWidth = cellWidth - cellPadding; // Available width minus padding

              switch (resizeDirection) {
                case "n":
                  newHeight = Math.max(50, startHeight.current - deltaY);
                  newY =
                    startImageY.current + (startHeight.current - newHeight);
                  break;
                case "s":
                  newHeight = Math.max(50, startHeight.current + deltaY);
                  break;
                case "e":
                  newWidth = Math.max(
                    50,
                    Math.min(maxImageWidth, startWidth.current + deltaX)
                  );
                  break;
                case "w":
                  newWidth = Math.max(
                    50,
                    Math.min(maxImageWidth, startWidth.current - deltaX)
                  );
                  newX = Math.max(
                    0,
                    Math.min(
                      startImageX.current + (startWidth.current - newWidth),
                      maxImageWidth - newWidth
                    )
                  );
                  break;
                case "ne":
                  newHeight = Math.max(50, startHeight.current - deltaY);
                  newWidth = Math.max(
                    50,
                    Math.min(maxImageWidth, startWidth.current + deltaX)
                  );
                  newY =
                    startImageY.current + (startHeight.current - newHeight);
                  break;
                case "nw":
                  newHeight = Math.max(50, startHeight.current - deltaY);
                  newWidth = Math.max(
                    50,
                    Math.min(maxImageWidth, startWidth.current - deltaX)
                  );
                  newY =
                    startImageY.current + (startHeight.current - newHeight);
                  newX = Math.max(
                    0,
                    Math.min(
                      startImageX.current + (startWidth.current - newWidth),
                      maxImageWidth - newWidth
                    )
                  );
                  break;
                case "se":
                  newHeight = Math.max(50, startHeight.current + deltaY);
                  newWidth = Math.max(
                    50,
                    Math.min(maxImageWidth, startWidth.current + deltaX)
                  );
                  break;
                case "sw":
                  newHeight = Math.max(50, startHeight.current + deltaY);
                  newWidth = Math.max(
                    50,
                    Math.min(maxImageWidth, startWidth.current - deltaX)
                  );
                  newX = Math.max(
                    0,
                    Math.min(
                      startImageX.current + (startWidth.current - newWidth),
                      maxImageWidth - newWidth
                    )
                  );
                  break;
              }

              return {
                ...img,
                width: newWidth,
                height: newHeight,
                x: newX,
                y: newY,
              };
            }
            return img;
          });

          // Recalculate positions to prevent overlap
          const sortedImages = updatedImages.sort((a, b) => a.y - b.y);
          const repositionedImages: Array<{
            id: string;
            src: string;
            width: number;
            height: number;
            x: number;
            y: number;
          }> = [];

          sortedImages.forEach((img, index) => {
            if (index === 0) {
              repositionedImages.push({ ...img, y: 0 });
            } else {
              const prevImage = repositionedImages[index - 1];
              const newY = prevImage.y + prevImage.height + 20; // 20px spacing
              repositionedImages.push({ ...img, y: newY });
            }
          });

          // Auto-adjust table height based on the tallest image
          const maxImageHeight = Math.max(
            ...repositionedImages.map((img) => img.y + img.height)
          );
          const newTableHeight = Math.max(150, maxImageHeight + 40);
          setHeight(newTableHeight);

          return repositionedImages;
        });
      }
    };

    const handleMouseUp = () => {
      if (isResizing) {
        setIsResizing(false);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      }
      if (isImageResizing) {
        setIsImageResizing(false);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      }
    };

    if (isResizing || isImageResizing) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isResizing, isImageResizing]);

  // Call onHeightChange when height changes
  useEffect(() => {
    if (onHeightChange) {
      onHeightChange(id, height);
    }
  }, [height, id, onHeightChange]);

  // Auto-resize images when table height changes
  useEffect(() => {
    if (leftColumnImages.length > 0) {
      const cellPadding = 20; // Account for cell padding
      const availableHeight = height - cellPadding;

      setLeftColumnImages((prevImages) => {
        return prevImages.map((image) => {
          // Check if image extends beyond available height
          const imageBottom = image.y + image.height;

          if (imageBottom > availableHeight) {
            // Calculate new height to fit within available space
            const newHeight = Math.max(50, availableHeight - image.y);
            const aspectRatio = image.width / image.height;
            const newWidth = newHeight * aspectRatio;

            // Ensure width doesn't exceed cell width
            const tableWidth = tableRef.current?.offsetWidth || 800;
            const cellWidth = tableWidth * 0.5;
            const maxWidth = cellWidth - 20; // Account for padding

            if (newWidth > maxWidth) {
              const finalWidth = maxWidth;
              const finalHeight = finalWidth / aspectRatio;
              return { ...image, width: finalWidth, height: finalHeight };
            }

            return { ...image, width: newWidth, height: newHeight };
          }

          return image;
        });
      });
    }
  }, [height, leftColumnImages.length]);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete && id !== "table-default") {
      onDelete(id);
    }
  };

  const handleMimic = () => {
    // This function will handle the mimic functionality
    console.log("Mimic button clicked - images to mimic:", leftColumnImages);
    // You can implement the mimic logic here
    // For example: copy images to right column, generate text based on images, etc.
  };

  return (
    <>
      <div
        ref={tableRef}
        className={`table-container relative ${
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
              onClick={handleCellClick}
            >
              {leftColumnImages.length === 0 ? (
                <div
                  {...getRootProps()}
                  className={`flex flex-col items-center justify-center h-full border-2 border-dashed rounded-lg transition-all duration-200 ${
                    isDragActive
                      ? "border-red-400 bg-red-50"
                      : "border-gray-300 hover:border-red-400 hover:bg-gray-50"
                  }`}
                >
                  <input {...getInputProps()} />
                  <div className="flex flex-col items-center gap-2 group">
                    <ImageIcon
                      size={32}
                      className={`transition-all duration-200 ${
                        isDragActive
                          ? "text-red-500 scale-110"
                          : "text-gray-400 group-hover:text-red-500 group-hover:scale-110"
                      }`}
                    />
                    <span
                      className={`font-medium transition-colors duration-200 ${
                        isDragActive ? "text-red-500" : "text-gray-600"
                      }`}
                    >
                      {isDragActive
                        ? "Drop images here"
                        : "Drag & drop images or click to upload"}
                    </span>
                  </div>
                </div>
              ) : (
                <div
                  {...getRootProps()}
                  className="relative w-full h-full"
                  onClick={() => setSelectedImageId(null)}
                >
                  <input {...getInputProps()} />
                  {leftColumnImages.map((image) => (
                    <div
                      key={image.id}
                      style={{
                        position: "absolute",
                        left: `${image.x}px`,
                        top: `${image.y}px`,
                        width: `${image.width}px`,
                        height: `${image.height}px`,
                        transition: "width 0.3s ease-out, height 0.3s ease-out",
                      }}
                      className="relative"
                    >
                      <img
                        src={image.src}
                        alt="Uploaded"
                        style={{
                          width: "100%",
                          height: "100%",
                          objectFit: "contain",
                          display: "block",
                        }}
                        className="cursor-pointer"
                        onClick={(e) => handleImageClick(e, image.id)}
                      />

                      {/* Resize anchors - 8 corners and edges - only show when selected */}
                      {selectedImageId === image.id && (
                        <>
                          {/* Top-left */}
                          <div
                            className="absolute -top-1 -left-1 w-3 h-3 bg-blue-500 cursor-nw-resize opacity-50 hover:opacity-100 transition-opacity z-50"
                            onMouseDown={(e) =>
                              handleImageMouseDown(e, image.id, "nw")
                            }
                          />
                          {/* Top */}
                          <div
                            className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-blue-500 cursor-n-resize opacity-50 hover:opacity-100 transition-opacity z-50"
                            onMouseDown={(e) =>
                              handleImageMouseDown(e, image.id, "n")
                            }
                          />
                          {/* Top-right */}
                          <div
                            className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 cursor-ne-resize opacity-50 hover:opacity-100 transition-opacity z-50"
                            onMouseDown={(e) =>
                              handleImageMouseDown(e, image.id, "ne")
                            }
                          />
                          {/* Right */}
                          <div
                            className="absolute top-1/2 -right-1 transform -translate-y-1/2 w-3 h-3 bg-blue-500 cursor-e-resize opacity-50 hover:opacity-100 transition-opacity z-50"
                            onMouseDown={(e) =>
                              handleImageMouseDown(e, image.id, "e")
                            }
                          />
                          {/* Bottom-right */}
                          <div
                            className="absolute -bottom-1 -right-1 w-3 h-3 bg-blue-500 cursor-se-resize opacity-50 hover:opacity-100 transition-opacity z-50"
                            onMouseDown={(e) =>
                              handleImageMouseDown(e, image.id, "se")
                            }
                          />
                          {/* Bottom */}
                          <div
                            className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-blue-500 cursor-s-resize opacity-50 hover:opacity-100 transition-opacity z-50"
                            onMouseDown={(e) =>
                              handleImageMouseDown(e, image.id, "s")
                            }
                          />
                          {/* Bottom-left */}
                          <div
                            className="absolute -bottom-1 -left-1 w-3 h-3 bg-blue-500 cursor-sw-resize opacity-50 hover:opacity-100 transition-opacity z-50"
                            onMouseDown={(e) =>
                              handleImageMouseDown(e, image.id, "sw")
                            }
                          />
                          {/* Left */}
                          <div
                            className="absolute top-1/2 -left-1 transform -translate-y-1/2 w-3 h-3 bg-blue-500 cursor-w-resize opacity-50 hover:opacity-100 transition-opacity z-50"
                            onMouseDown={(e) =>
                              handleImageMouseDown(e, image.id, "w")
                            }
                          />
                        </>
                      )}

                      {/* Remove image button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setLeftColumnImages((prev) => {
                            const filteredImages = prev.filter(
                              (img) => img.id !== image.id
                            );

                            // Reposition remaining images to prevent gaps
                            const repositionedImages: Array<{
                              id: string;
                              src: string;
                              width: number;
                              height: number;
                              x: number;
                              y: number;
                            }> = [];

                            filteredImages.forEach((img, index) => {
                              if (index === 0) {
                                repositionedImages.push({ ...img, y: 0 });
                              } else {
                                const prevImage = repositionedImages[index - 1];
                                const newY =
                                  prevImage.y + prevImage.height + 20; // 20px spacing
                                repositionedImages.push({ ...img, y: newY });
                              }
                            });

                            // Adjust table height
                            if (repositionedImages.length === 0) {
                              setHeight(300);
                            } else {
                              const maxImageHeight = Math.max(
                                ...repositionedImages.map(
                                  (img) => img.y + img.height
                                )
                              );
                              const newTableHeight = Math.max(
                                150,
                                maxImageHeight + 40
                              );
                              setHeight(newTableHeight);
                            }

                            return repositionedImages;
                          });
                        }}
                        className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors flex items-center justify-center z-50"
                      >
                        <X size={12} />
                      </button>
                    </div>
                  ))}

                  {/* Upload more button */}
                  <div className="absolute bottom-0 left-0 right-0 p-2">
                    <div
                      {...getRootProps()}
                      className="cursor-pointer bg-white hover:bg-gray-50 text-gray-600 hover:text-red-500 px-2 py-1 rounded-md text-sm transition-all duration-300 shadow-sm hover:shadow-md text-center w-8 h-8 flex items-center justify-center group border border-gray-200 hover:border-red-300 mx-auto"
                    >
                      <input {...getInputProps()} />
                      <div className="relative">
                        <Upload
                          size={16}
                          className="group-hover:scale-110 transition-all duration-300 ease-out"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right Cell */}
            <RightColumn
              height={height}
              hasImages={leftColumnImages.length > 0}
              onMimic={handleMimic}
              onCellClick={handleCellClick}
              onDeselectImage={() => setSelectedImageId(null)}
            />
          </div>
        </div>
      </div>
    </>
  );
};
