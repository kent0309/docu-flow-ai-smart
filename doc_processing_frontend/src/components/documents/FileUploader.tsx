import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Upload, X, FileType } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const FileUploader = () => {
  const [files, setFiles] = useState<Array<File & { preview?: string }>>([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prevFiles => [...prevFiles, ...acceptedFiles.map(file => Object.assign(file, {
      preview: URL.createObjectURL(file)
    }))]);
    toast.success(`${acceptedFiles.length} file(s) added to the queue.`);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10485760, // 10MB
  });

  const removeFile = (fileToRemove: File) => {
    setFiles(files => files.filter(file => file !== fileToRemove));
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      toast.error('Please add at least one file to upload.');
      return;
    }

    setUploading(true);
    toast.info(`Uploading ${files.length} file(s)...`);

    const uploadPromises = files.map(file => {
      const formData = new FormData();
      // The key 'uploaded_file' must match what the Django backend API expects.
      formData.append('uploaded_file', file);

      // The actual fetch request to your Django backend API
      return fetch('http://127.0.0.1:8000/api/documents/upload/', {
        method: 'POST',
        body: formData,
      });
    });

    try {
      const responses = await Promise.all(uploadPromises);
      
      let allSuccess = true;
      for (const res of responses) {
        if (!res.ok) {
          allSuccess = false;
          console.error('An upload failed:', await res.json());
        }
      }

      if (allSuccess) {
        toast.success(`${files.length} file(s) uploaded successfully!`);
      } else {
        toast.error('Some files failed to upload. See console for details.');
      }

    } catch (error) {
      console.error('Upload error:', error);
      toast.error('A connection error occurred. Is the backend server running?');
    } finally {
      setUploading(false);
      setFiles([]); // Clear the file list after attempting upload
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full space-y-6">
      <div 
        {...getRootProps()} 
        className={cn(
          "file-drop-area p-8 cursor-pointer text-center transition-all",
          isDragActive ? "active" : ""
        )}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center gap-4">
          <div className="rounded-full bg-primary/10 p-4">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-1">
              {isDragActive ? "Drop files here..." : "Drag & Drop files here"}
            </h3>
            <p className="text-sm text-muted-foreground">
              or click to browse
            </p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Selected Files ({files.length})</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center gap-4 p-3 bg-secondary rounded-md">
                <div className="rounded-md bg-primary/10 p-2">
                  <FileType className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => removeFile(file)}
                  disabled={uploading}
                  className="text-muted-foreground hover:text-destructive"
                >
                  <X className="h-4 w-4" />
                  <span className="sr-only">Remove</span>
                </Button>
              </div>
            ))}
          </div>

          {uploading ? (
            <div className="space-y-2">
              <div className="flex justify-between text-sm font-medium">
                <span>Uploading... Please wait.</span>
              </div>
              <Progress value={100} className="h-2 animate-pulse" />
            </div>
          ) : (
            <Button onClick={uploadFiles} className="w-full">
              Upload & Process Files
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
