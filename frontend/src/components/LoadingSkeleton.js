/**
 * Loading Skeleton Components
 * Provides visual feedback while content is loading
 */
import React from 'react';

// Base skeleton component
export const Skeleton = ({ className = '', height = '20px', width = '100%', rounded = 'md' }) => {
  const roundedClasses = {
    none: '',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full'
  };
  
  return (
    <div 
      className={`animate-pulse bg-gray-200 dark:bg-gray-700 ${roundedClasses[rounded]} ${className}`}
      style={{ height, width }}
    />
  );
};

// Card skeleton
export const CardSkeleton = () => {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
      <Skeleton height="24px" width="70%" className="mb-4" />
      <Skeleton height="16px" width="100%" className="mb-2" />
      <Skeleton height="16px" width="90%" className="mb-2" />
      <Skeleton height="16px" width="80%" className="mb-4" />
      <div className="flex gap-2 mt-4">
        <Skeleton height="32px" width="80px" rounded="md" />
        <Skeleton height="32px" width="80px" rounded="md" />
      </div>
    </div>
  );
};

// Table skeleton
export const TableSkeleton = ({ rows = 5, columns = 4 }) => {
  return (
    <div className="w-full">
      {/* Table header */}
      <div className="flex gap-4 mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
        {Array.from({ length: columns }).map((_, idx) => (
          <div key={idx} className="flex-1">
            <Skeleton height="20px" width="80%" />
          </div>
        ))}
      </div>
      
      {/* Table rows */}
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="flex gap-4 mb-3 pb-3 border-b border-gray-100 dark:border-gray-800">
          {Array.from({ length: columns }).map((_, colIdx) => (
            <div key={colIdx} className="flex-1">
              <Skeleton height="18px" width={`${60 + Math.random() * 30}%`} />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

// Profile skeleton
export const ProfileSkeleton = () => {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
      <div className="flex items-center gap-4 mb-6">
        <Skeleton height="80px" width="80px" rounded="full" />
        <div className="flex-1">
          <Skeleton height="24px" width="60%" className="mb-2" />
          <Skeleton height="16px" width="40%" />
        </div>
      </div>
      <Skeleton height="16px" width="100%" className="mb-2" />
      <Skeleton height="16px" width="90%" className="mb-2" />
      <Skeleton height="16px" width="95%" className="mb-4" />
      <div className="grid grid-cols-3 gap-4 mt-4">
        <div>
          <Skeleton height="16px" width="60%" className="mb-2" />
          <Skeleton height="24px" width="80%" />
        </div>
        <div>
          <Skeleton height="16px" width="60%" className="mb-2" />
          <Skeleton height="24px" width="80%" />
        </div>
        <div>
          <Skeleton height="16px" width="60%" className="mb-2" />
          <Skeleton height="24px" width="80%" />
        </div>
      </div>
    </div>
  );
};

// List skeleton
export const ListSkeleton = ({ items = 5 }) => {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, idx) => (
        <div key={idx} className="flex items-center gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg">
          <Skeleton height="40px" width="40px" rounded="md" />
          <div className="flex-1">
            <Skeleton height="18px" width="70%" className="mb-2" />
            <Skeleton height="14px" width="50%" />
          </div>
          <Skeleton height="32px" width="60px" rounded="md" />
        </div>
      ))}
    </div>
  );
};

// Dashboard skeleton
export const DashboardSkeleton = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Skeleton height="32px" width="40%" className="mb-2" />
        <Skeleton height="20px" width="60%" />
      </div>
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, idx) => (
          <div key={idx} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <Skeleton height="16px" width="60%" className="mb-3" />
            <Skeleton height="32px" width="80%" className="mb-2" />
            <Skeleton height="14px" width="50%" />
          </div>
        ))}
      </div>
      
      {/* Content area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    </div>
  );
};

// Form skeleton
export const FormSkeleton = ({ fields = 5 }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: fields }).map((_, idx) => (
        <div key={idx}>
          <Skeleton height="16px" width="30%" className="mb-2" />
          <Skeleton height="40px" width="100%" rounded="md" />
        </div>
      ))}
      <div className="flex gap-3 mt-6">
        <Skeleton height="40px" width="120px" rounded="md" />
        <Skeleton height="40px" width="120px" rounded="md" />
      </div>
    </div>
  );
};

// Grid skeleton (for image galleries, etc.)
export const GridSkeleton = ({ items = 12, columns = 4 }) => {
  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 md:grid-cols-${columns} gap-4`}>
      {Array.from({ length: items }).map((_, idx) => (
        <div key={idx} className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-md">
          <Skeleton height="200px" width="100%" rounded="none" />
          <div className="p-4">
            <Skeleton height="18px" width="80%" className="mb-2" />
            <Skeleton height="14px" width="60%" />
          </div>
        </div>
      ))}
    </div>
  );
};

// Page loading overlay
export const PageLoadingOverlay = ({ message = 'Loading...' }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
        <p className="text-gray-700 dark:text-gray-300">{message}</p>
      </div>
    </div>
  );
};

export default Skeleton;
