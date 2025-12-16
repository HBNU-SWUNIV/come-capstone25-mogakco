import React, { createContext, useContext, type ReactNode } from 'react';
import { useGlobalDocumentPolling } from '../hooks/use-global-document-polling';

interface DocumentPollingContextType {
	addProcessingDocument: (jobId: string, fileName?: string) => void;
	removeProcessingDocument: (jobId: string) => void;
	startPolling: () => void;
	stopPolling: () => void;
	getProcessingDocuments: () => Array<{
		jobId: string;
		fileName?: string;
		startedAt: number;
	}>;
	isPolling: () => boolean;
}

const DocumentPollingContext = createContext<DocumentPollingContextType | null>(
	null,
);

interface DocumentPollingProviderProps {
	children: ReactNode;
}

export const DocumentPollingProvider = ({
	children,
}: DocumentPollingProviderProps) => {
	const polling = useGlobalDocumentPolling();

	return (
		<DocumentPollingContext.Provider value={polling}>
			{children}
		</DocumentPollingContext.Provider>
	);
};

export const useDocumentPolling = () => {
	const context = useContext(DocumentPollingContext);
	if (!context) {
		throw new Error(
			'useDocumentPolling must be used within a DocumentPollingProvider',
		);
	}
	return context;
};
