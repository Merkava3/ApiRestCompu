import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from '@/components/ui/carousel';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ShoppingCart, Check, X } from 'lucide-react';
import { useCart } from '@/contexts/CartContext';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  quantity: number;
  availability: 'in-stock' | 'limited' | 'out-of-stock';
  images: string[];
  category: string;
}

interface ProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  category: {
    title: string;
    products: string[];
  };
}

const ProductModal = ({ isOpen, onClose, category }: ProductModalProps) => {
  const { addToCart } = useCart();
  
  // Sample product data - in a real app this would come from an API
  const getProductsForCategory = (categoryTitle: string): Product[] => {
    const baseProducts = {
      "Keyboards": [
        {
          id: "kb-001",
          name: "Mechanical Gaming Keyboard RGB",
          description: "High-performance mechanical keyboard with RGB backlighting, Cherry MX switches, and programmable keys. Perfect for gaming and professional use.",
          price: 149.99,
          quantity: 15,
          availability: "in-stock" as const,
          images: [
            "https://images.unsplash.com/photo-1541140532154-b024d705b90a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1587829741301-dc798b83add3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1595044426077-d36d9236d54a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
          ],
          category: "Keyboards"
        },
        {
          id: "kb-002",
          name: "Wireless Ergonomic Keyboard",
          description: "Comfortable wireless keyboard designed for long typing sessions. Features split layout and wrist support.",
          price: 89.99,
          quantity: 8,
          availability: "limited" as const,
          images: [
            "https://images.unsplash.com/photo-1587829741301-dc798b83add3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1541140532154-b024d705b90a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
          ],
          category: "Keyboards"
        }
      ],
      "Computer Mice": [
        {
          id: "ms-001",
          name: "Precision Gaming Mouse",
          description: "High-DPI gaming mouse with customizable buttons and RGB lighting. Features adjustable weight system.",
          price: 79.99,
          quantity: 22,
          availability: "in-stock" as const,
          images: [
            "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1563297007-0686b7003af7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1541140532154-b024d705b90a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
          ],
          category: "Computer Mice"
        }
      ],
      "Webcams": [
        {
          id: "wc-001",
          name: "4K Streaming Webcam",
          description: "Professional 4K webcam with auto-focus and noise-canceling microphone. Perfect for streaming and video calls.",
          price: 199.99,
          quantity: 0,
          availability: "out-of-stock" as const,
          images: [
            "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
          ],
          category: "Webcams"
        }
      ],
      "Computer Accessories": [
        {
          id: "ca-001",
          name: "USB-C Hub with 7 Ports",
          description: "Versatile USB-C hub with multiple ports including HDMI, USB 3.0, and SD card reader.",
          price: 49.99,
          quantity: 35,
          availability: "in-stock" as const,
          images: [
            "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1595044426077-d36d9236d54a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
          ],
          category: "Computer Accessories"
        }
      ]
    };

    return baseProducts[categoryTitle as keyof typeof baseProducts] || [];
  };

  const products = getProductsForCategory(category.title);
  const [selectedProduct, setSelectedProduct] = useState(products[0] || null);

  const getAvailabilityBadge = (availability: Product['availability']) => {
    switch (availability) {
      case 'in-stock':
        return <Badge className="bg-green-100 text-green-800 border-green-200"><Check className="w-3 h-3 mr-1" />In Stock</Badge>;
      case 'limited':
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">Limited Stock</Badge>;
      case 'out-of-stock':
        return <Badge className="bg-red-100 text-red-800 border-red-200"><X className="w-3 h-3 mr-1" />Out of Stock</Badge>;
    }
  };

  const handleAddToCart = () => {
    if (selectedProduct && selectedProduct.availability !== 'out-of-stock') {
      addToCart({
        id: selectedProduct.id,
        name: selectedProduct.name,
        price: selectedProduct.price,
        image: selectedProduct.images[0]
      });
      console.log('Added to cart:', selectedProduct.name);
    }
  };

  if (!selectedProduct) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[70vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold text-slate-800">{category.title}</DialogTitle>
        </DialogHeader>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Left side - Product Images Gallery/Carousel */}
          <div className="space-y-3">
            <div className="relative">
              <Carousel className="w-full">
                <CarouselContent>
                  {selectedProduct.images.map((image, index) => (
                    <CarouselItem key={index}>
                      <div className="aspect-square overflow-hidden rounded-lg border border-navy-200 bg-white">
                        <img
                          src={image}
                          alt={`${selectedProduct.name} - Image ${index + 1}`}
                          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                        />
                      </div>
                    </CarouselItem>
                  ))}
                </CarouselContent>
                {selectedProduct.images.length > 1 && (
                  <>
                    <CarouselPrevious className="left-1" />
                    <CarouselNext className="right-1" />
                  </>
                )}
              </Carousel>
              
              {/* Image counter */}
              {selectedProduct.images.length > 1 && (
                <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 bg-black/70 text-white px-2 py-1 rounded-md text-xs">
                  {selectedProduct.images.length} images
                </div>
              )}
            </div>
            
            {/* Product Selection */}
            {products.length > 1 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-slate-700 text-xs">Available Products:</h4>
                <div className="grid grid-cols-1 gap-1 max-h-24 overflow-y-auto">
                  {products.map((product) => (
                    <button
                      key={product.id}
                      onClick={() => setSelectedProduct(product)}
                      className={`p-2 text-left rounded-lg border transition-colors text-xs ${
                        selectedProduct.id === product.id
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 hover:border-green-300'
                      }`}
                    >
                      <div className="font-medium truncate">{product.name}</div>
                      <div className="text-xs text-gray-600">${product.price}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right side - Product Information */}
          <div className="space-y-3">
            <div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">{selectedProduct.name}</h3>
              <p className="text-gray-600 text-xs leading-relaxed">{selectedProduct.description}</p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-700 text-sm">Price:</span>
                <span className="text-lg font-bold text-green-600">${selectedProduct.price}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-700 text-sm">Quantity:</span>
                <span className="font-medium text-sm">{selectedProduct.quantity} units</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-700 text-sm">Availability:</span>
                {getAvailabilityBadge(selectedProduct.availability)}
              </div>
            </div>

            <div className="pt-3 space-y-2">
              <Button 
                className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-sm"
                disabled={selectedProduct.availability === 'out-of-stock'}
                onClick={handleAddToCart}
              >
                <ShoppingCart className="w-4 h-4 mr-2" />
                {selectedProduct.availability === 'out-of-stock' ? 'Out of Stock' : 'Add to Cart'}
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full border-green-500 text-green-600 hover:bg-green-50 text-sm"
                disabled={selectedProduct.availability === 'out-of-stock'}
              >
                Contact for Quote
              </Button>
            </div>

            <div className="pt-2 border-t border-gray-200">
              <p className="text-xs text-gray-500">
                Need help choosing? Contact our experts for recommendations.
              </p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ProductModal;
