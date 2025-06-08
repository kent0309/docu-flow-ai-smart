
# Document Processing Frontend

A modern React frontend application for AI-powered document processing.

## Features

- **Document Upload**: Drag & drop interface for uploading documents
- **Real-time Processing**: Monitor document processing status in real-time
- **Analytics Dashboard**: Comprehensive analytics and insights
- **Document Management**: View, search, and organize processed documents
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Technology Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - Beautiful and accessible UI components
- **React Router** - Client-side routing
- **React Query** - Data fetching and state management
- **React Dropzone** - File upload functionality
- **Recharts** - Data visualization
- **Lucide React** - Beautiful icons

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doc_processing_frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Shadcn/UI components
│   ├── layout/         # Layout components
│   └── documents/      # Document-specific components
├── pages/              # Page components
├── services/           # API services and mock data
├── types/              # TypeScript type definitions
├── lib/                # Utility functions
└── hooks/              # Custom React hooks
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Key Components

### FileUploader
Handles document upload with drag & drop functionality, progress tracking, and file validation.

### DocumentCard
Displays document information including processing status, confidence scores, and extracted data.

### Layout
Responsive sidebar navigation with mobile support.

### Analytics Dashboard
Interactive charts and metrics for processing insights.

## Mock Services

The application uses mock services to simulate backend functionality:

- Document management (CRUD operations)
- Processing statistics
- File upload simulation
- Search and filtering

## Styling

The application uses Tailwind CSS with a custom design system defined in `src/index.css`. All components follow the design tokens for consistent theming.

## Type Safety

Full TypeScript support with comprehensive type definitions for:
- Document objects
- Processing statistics
- API responses
- Component props

## Responsive Design

The application is fully responsive and works across:
- Desktop (1024px+)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## Future Enhancements

- Real backend integration
- User authentication
- Advanced document processing options
- Batch processing capabilities
- Export functionality
- Advanced analytics
