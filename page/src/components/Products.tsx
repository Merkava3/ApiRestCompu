
import { useState } from 'react';
import { Mouse, Keyboard, Webcam, Computer } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import ProductModal from './ProductModal';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/components/ui/carousel';

const productCategories = [
  {
    icon: Keyboard,
    title: "Keyboards",
    description: "Mechanical and wireless keyboards for gaming and productivity",
    products: ["Gaming Keyboards", "Wireless Keyboards", "Ergonomic Keyboards", "Mechanical Switches"],
    image: "https://images.unsplash.com/photo-1541140532154-b024d705b90a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
  },
  {
    icon: Mouse,
    title: "Computer Mice",
    description: "Precision mice for all your computing needs",
    products: ["Gaming Mice", "Wireless Mice", "Ergonomic Mice", "Trackballs"],
    image: "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
  },
  {
    icon: Webcam,
    title: "Webcams",
    description: "High-quality webcams for video calls and streaming",
    products: ["HD Webcams", "4K Webcams", "Streaming Cameras", "Conference Cameras"],
    image: "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
  },
  {
    icon: Computer,
    title: "Computer Accessories",
    description: "Essential accessories to enhance your computing experience",
    products: ["USB Hubs", "Cable Management", "Monitor Stands", "Laptop Stands"],
    image: "https://images.unsplash.com/photo-1518770660439-4636190af475?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
  }
  // Add more categories here to test infinite carousel
];

const Products = () => {
  const [selectedCategory, setSelectedCategory] = useState<typeof productCategories[0] | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleViewProducts = (category: typeof productCategories[0]) => {
    setSelectedCategory(category);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedCategory(null);
  };

  return (
    <section className="py-20 px-4 bg-white w-full">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-slate-800 mb-4 animate-fade-in">Technology Products</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto animate-fade-in" style={{ animationDelay: '0.2s' }}>
            Quality technology products and accessories from trusted brands
          </p>
        </div>
        {/* Carousel for product categories */}
        <Carousel
          className="w-full max-w-4xl mx-auto relative"
          opts={{
            loop: true,
            align: 'start',
            skipSnaps: true,
            draggable: true,
          }}
        >
          <CarouselContent>
            {productCategories.map((category, index) => (
              <CarouselItem
                key={index}
                className="basis-72 md:basis-80 lg:basis-96"
              >
                <Card className="group overflow-hidden relative border-green-200 hover:shadow-xl transition-all duration-300 
                  animate-fade-in opacity-0 will-change-transform"
                  style={{ animationDelay: `${0.08 * index}s`, animationFillMode: 'forwards' }}
                >
                  <div className="relative h-36 overflow-hidden rounded-lg">
                    <img 
                      src={category.image} 
                      alt={category.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 left-3 bg-white/90 p-1.5 rounded-full">
                      <category.icon className="w-5 h-5 text-green-600" />
                    </div>
                  </div>
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg text-slate-800">{category.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4 pt-0">
                    <p className="text-sm text-gray-600 mb-2">{category.description}</p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {category.products.map((product, productIndex) => (
                        <div key={productIndex} className="bg-green-50 px-2 py-1 rounded text-xs text-slate-700 border border-green-100">
                          {product}
                        </div>
                      ))}
                    </div>
                    <Button 
                      className="w-full py-2 px-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-sm rounded-lg"
                      onClick={() => handleViewProducts(category)}
                    >
                      View Products
                    </Button>
                  </CardContent>
                </Card>
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
        
        {/* CTA section remains */}
        <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-2xl p-8 text-center border border-green-200 mt-10 animate-fade-in"
          style={{ animationDelay: '0.6s' }}
        >
          <h3 className="text-2xl font-bold text-slate-800 mb-2">Need Help Choosing?</h3>
          <p className="text-gray-600 mb-4 max-w-2xl mx-auto">
            Our experts can help you find the perfect technology products for your needs. 
            Get personalized recommendations based on your requirements and budget.
          </p>
          <Button size="lg" className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700">
            Get Expert Advice
          </Button>
        </div>
      </div>
      {/* Product Modal */}
      {selectedCategory && (
        <ProductModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          category={selectedCategory}
        />
      )}
    </section>
  );
};

export default Products;
