
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { UploadedFile } from '@/types';
import { mockService } from '@/services/mockService';

const FileUploader = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      ...file,
      id: Math.random().toString(36).substr(2, 9),
      preview: URL.createObjectURL(file),
      uploadProgress: 0,
      status: 'uploading' as const
    }));
    
    setFiles(prev => [...prev, ...newFiles]);
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

  const removeFile = (id: string) => {
    setFiles(prev => {
      const newFiles = prev.filter(file => file.id !== id);
      const fileToRemove = prev.find(file => file.id === id);
      if (fileToRemove?.preview) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return newFiles;
    });
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      toast.error('Please add at least one file to upload');
      return;
    }
    
    setUploading(true);
    
    try {
      for (const file of files) {
        // Simulate upload progress
        for (let progress = 0; progress <= 100; progress += 10) {
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, uploadProgress: progress } : f
          ));
          await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        // Upload file using mock service
        await mockService.uploadDocument(file);
        
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'uploaded' } : f
        ));
      }
      
      toast.success('All files uploaded successfully!');
      
      // Clear files after successful upload
      setTimeout(() => {
        setFiles([]);
      }, 2000);
      
    } catch (error) {
      toast.error('Upload failed. Please try again.');
      setFiles(prev => prev.map(f => ({ ...f, status: 'error' })));
    } finally {
      setUploading(false);
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
    <div className="space-y-6">
      {/* Drop zone */}
      <Card>
        <CardContent className="p-6">
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
        </CardContent>
      </Card>

      {/* File list */}
      {files.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Selected Files ({files.length})</h3>
              <div className="space-y-3">
                {files.map((file) => (
                  <div key={file.id} className="flex items-center gap-4 p-3 bg-muted rounded-md">
                    <div className="rounded-md bg-primary/10 p-2">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{file.name}</p>
                      <p className="text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
                      
                      {file.status === 'uploading' && (
                        <div className="mt-2">
                          <Progress value={file.uploadProgress || 0} className="h-1" />
                          <p className="text-xs text-muted-foreground mt-1">
                            Uploading... {file.uploadProgress || 0}%
                          </p>
                        </div>
                      )}
                      
                      {file.status === 'uploaded' && (
                        <div className="flex items-center gap-1 mt-1">
                          <CheckCircle className="h-3 w-3 text-green-500" />
                          <span className="text-xs text-green-600">Uploaded</span>
                        </div>
                      )}
                      
                      {file.status === 'error' && (
                        <div className="flex items-center gap-1 mt-1">
                          <AlertCircle className="h-3 w-3 text-red-500" />
                          <span className="text-xs text-red-600">Failed</span>
                        </div>
                      )}
                    </div>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => removeFile(file.id)}
                      disabled={uploading}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>

              {!uploading ? (
                <Button onClick={uploadFiles} className="w-full">
                  <Upload className="h-4 w-4 mr-2" />
                  Upload & Process Files
                </Button>
              ) : (
                <Button disabled className="w-full">
                  Processing...
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FileUploader;
