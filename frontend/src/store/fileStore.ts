import { create } from 'zustand'
import { File } from '../services/fileService'

interface FileState {
  files: File[]
  currentFolderId: string | null
  setFiles: (files: File[]) => void
  setCurrentFolder: (folderId: string | null) => void
  addFile: (file: File) => void
  removeFile: (fileId: string) => void
}

export const useFileStore = create<FileState>((set) => ({
  files: [],
  currentFolderId: null,
  setFiles: (files) => set({ files }),
  setCurrentFolder: (folderId) => set({ currentFolderId: folderId }),
  addFile: (file) => set((state) => ({ files: [...state.files, file] })),
  removeFile: (fileId) =>
    set((state) => ({
      files: state.files.filter((f) => f.id !== fileId),
    })),
}))
