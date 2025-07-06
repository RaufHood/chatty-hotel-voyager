const API_BASE_URL = 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  reply: string;
  session_id: string;
  tools_used: string[] | null;
  hotel_data: any[] | null;
  selected_hotel: any | null;
  timestamp: string;
}

export interface Hotel {
  id: string;
  name: string;
  location: string;
  price: number;
  rating: number;
  image: string;
  amenities: string[];
  description: string;
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Chat API error:', error);
      // Return a fallback response if the API is not available
      return {
        reply: "I'm having trouble connecting to my services right now. Please try again later.",
        session_id: request.session_id,
        tools_used: null,
        hotel_data: null,
        selected_hotel: null,
        timestamp: new Date().toISOString(),
      };
    }
  }

  async getChatHistory(sessionId: string): Promise<ChatResponse[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/history/${sessionId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get chat history error:', error);
      return [];
    }
  }

  async clearChatHistory(sessionId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/history/${sessionId}`, {
        method: 'DELETE',
      });
      
      return response.ok;
    } catch (error) {
      console.error('Clear chat history error:', error);
      return false;
    }
  }

  async searchHotels(query: string): Promise<Hotel[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/hotels/search?q=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Hotel search error:', error);
      return [];
    }
  }

  async getHotelDetails(hotelId: string): Promise<Hotel | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/hotels/${hotelId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get hotel details error:', error);
      return null;
    }
  }
}

export const apiService = new ApiService(); 