
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Upload, X, FileType, Check } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const FileUploader = () => {
  const [files, setFiles] = useState<Array<File & { preview?: string }>>([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(
      acceptedFiles.map(file => 
        Object.assign(file, {
          preview: URL.createObjectURL(file)
        })
      )
    );
    
    toast.success(`${acceptedFiles.length} file${acceptedFiles.length !== 1 ? 's' : ''} added`);
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

  const removeFile = (index: number) => {
    setFiles(files => {
      const newFiles = [...files];
      URL.revokeObjectURL(newFiles[index].preview as string);
      newFiles.splice(index, 1);
      return newFiles;
    });
  };

  const uploadFiles = () => {
    if (files.length === 0) {
      toast.error('Please add at least one file to upload');
      return;
    }
    
    setUploading(true);
    setProgress(0);
    
    // Simulate upload progress
    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + 5;
        if (newProgress >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setUploading(false);
            toast.success('Files processed successfully!');
            setFiles([]);
          }, 500);
          return 100;
        }
        return newProgress;
      });
    }, 200);
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
          isDragActive ? "active" : "",
          uploading ? "opacity-50 pointer-events-none" : ""
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
              or click to browse (PDF, JPG, PNG, DOC, DOCX - Max 10MB)
            </p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Selected Files ({files.length})</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center gap-4 p-3 bg-background border rounded-md">
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
                  onClick={() => removeFile(index)}
                  disabled={uploading}
                  className="text-muted-foreground hover:text-foreground"
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
                <span>Uploading and Processing...</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
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
