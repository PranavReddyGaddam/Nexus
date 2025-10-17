import React, { useRef } from 'react';
import { Paperclip, X, File } from 'lucide-react';

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  selectedFiles: File[];
  onRemoveFile: (index: number) => void;
}

export default function FileUpload({ onFilesSelected, selectedFiles, onRemoveFile }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    onFilesSelected(files);
    // Reset input so the same file can be selected again
    event.target.value = '';
  };

  return (
    <div className="relative">
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        multiple
        accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.json"
      />

      {/* Attach button */}
      <button
        onClick={handleClick}
        className="w-9 h-9 flex items-center justify-center text-gray-400 bg-gray-800 border border-gray-600 rounded-full cursor-pointer hover:bg-gray-700 transition-colors"
        aria-label="Attach files"
      >
        <Paperclip size={18} />
      </button>

      {/* Selected files preview */}
      {selectedFiles.length > 0 && (
        <div className="absolute bottom-full left-0 mb-2 w-64 bg-gray-800 rounded-lg border border-gray-700 p-2 space-y-1">
          {selectedFiles.map((file, index) => (
            <div
              key={`${file.name}-${index}`}
              className="flex items-center justify-between bg-gray-900 rounded px-2 py-1 text-sm"
            >
              <div className="flex items-center gap-2 truncate">
                <File size={14} className="text-blue-400 flex-shrink-0" />
                <span className="text-gray-300 truncate" title={file.name}>
                  {file.name}
                </span>
              </div>
              <button
                onClick={() => onRemoveFile(index)}
                className="text-gray-500 hover:text-gray-300 ml-2"
                aria-label={`Remove ${file.name}`}
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
