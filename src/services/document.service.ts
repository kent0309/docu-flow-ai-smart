
import { toast } from "sonner";

export class DocumentService {
  static async summarizeDocument(documentId: string): Promise<{ summary: string }> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock summary based on document ID
    let summaryText = '';
    
    if (documentId === '1') {
      summaryText = `Executive Summary:\n\n` +
        `This invoice dated May 8, 2025 from Tech Supplies Inc. details a purchase of office equipment ` +
        `totaling $1,245.67 with payment due by June 15, 2025. The order includes 5 laptops, 3 monitors, ` +
        `and various peripherals. A 5% discount was applied for bulk purchase.\n\n` +
        `• Purchase Order: PO-2025-789\n` +
        `• Invoice Number: INV-2025-0042\n` +
        `• Tax Amount: $98.76\n` +
        `• Shipping: $35.00\n`;
    } else {
      summaryText = `Executive Summary:\n\n` +
        `This document discusses key financial metrics for Q3 2023, highlighting a 15% increase in revenue compared to Q2. ` +
        `Major points include:\n\n` +
        `• Revenue growth primarily driven by expansion in Asian markets\n` +
        `• Operating costs reduced by 8% due to automation initiatives\n` +
        `• New product line exceeded sales targets by 22%\n` +
        `• Customer retention improved to 94% (up from 89%)\n\n` +
        `The document recommends continued investment in automation and expansion of the product line to additional markets in Q4.`;
    }
    
    return { summary: summaryText };
  }
}
