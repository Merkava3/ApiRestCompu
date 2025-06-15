
import { useState } from 'react';
import { MessageSquare, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

const ChatButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messageCount] = useState(3); // Mock message count

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Message sent');
    // Handle message submission
  };

  return (
    <>
      {/* Floating Chat Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={toggleChat}
          className="relative w-14 h-14 rounded-full bg-green-600 hover:bg-green-700 shadow-lg"
          size="icon"
        >
          {isOpen ? (
            <X className="w-6 h-6" />
          ) : (
            <>
              <MessageSquare className="w-6 h-6" />
              {messageCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
                  {messageCount}
                </span>
              )}
            </>
          )}
        </Button>
      </div>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-80 max-h-96">
          <Card className="shadow-2xl border-green-200">
            <CardHeader className="bg-green-600 text-white rounded-t-lg">
              <CardTitle className="text-lg">Chat with Us</CardTitle>
            </CardHeader>
            <CardContent className="p-4 max-h-80 overflow-y-auto">
              <div className="space-y-4 mb-4">
                <div className="bg-gray-100 p-3 rounded-lg">
                  <p className="text-sm">Hello! How can we help you today?</p>
                </div>
                <div className="bg-gray-100 p-3 rounded-lg">
                  <p className="text-sm">Do you have any questions about our services?</p>
                </div>
                <div className="bg-gray-100 p-3 rounded-lg">
                  <p className="text-sm">We're here to assist you!</p>
                </div>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-3">
                <Textarea 
                  placeholder="Type your message..." 
                  rows={3}
                  className="resize-none"
                />
                <Button 
                  type="submit" 
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  Send Message
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
};

export default ChatButton;
