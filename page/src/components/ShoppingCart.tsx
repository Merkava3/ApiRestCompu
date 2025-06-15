
import { useState } from 'react';
import { ShoppingCart, X, Plus, Minus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useCart } from '@/contexts/CartContext';

const ShoppingCartButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { items, getTotalItems, getTotalPrice, updateQuantity, removeFromCart } = useCart();

  const toggleCart = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating Cart Button */}
      <div className="fixed bottom-6 left-6 z-50">
        <Button
          onClick={toggleCart}
          className="relative w-14 h-14 rounded-full bg-blue-600 hover:bg-blue-700 shadow-lg"
          size="icon"
        >
          <ShoppingCart className="w-6 h-6" />
          {getTotalItems() > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
              {getTotalItems()}
            </span>
          )}
        </Button>
      </div>

      {/* Cart Window */}
      {isOpen && (
        <div className="fixed bottom-24 left-6 z-50 w-96 max-h-96">
          <Card className="shadow-2xl border-blue-200">
            <CardHeader className="bg-blue-600 text-white rounded-t-lg flex flex-row items-center justify-between">
              <CardTitle className="text-lg">Shopping Cart</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleCart}
                className="text-white hover:bg-blue-700"
              >
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="p-4 max-h-80 overflow-y-auto">
              {items.length === 0 ? (
                <p className="text-gray-500 text-center py-4">Your cart is empty</p>
              ) : (
                <div className="space-y-4">
                  {items.map((item) => (
                    <div key={item.id} className="flex items-center space-x-3 border-b pb-3">
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-12 h-12 object-cover rounded"
                      />
                      <div className="flex-1">
                        <h4 className="font-medium text-sm">{item.name}</h4>
                        <p className="text-green-600 font-semibold">${item.price}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="icon"
                          className="w-6 h-6"
                          onClick={() => updateQuantity(item.id, item.cartQuantity - 1)}
                        >
                          <Minus className="w-3 h-3" />
                        </Button>
                        <span className="text-sm font-medium">{item.cartQuantity}</span>
                        <Button
                          variant="outline"
                          size="icon"
                          className="w-6 h-6"
                          onClick={() => updateQuantity(item.id, item.cartQuantity + 1)}
                        >
                          <Plus className="w-3 h-3" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="w-6 h-6 text-red-500 hover:text-red-700"
                          onClick={() => removeFromCart(item.id)}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  <div className="border-t pt-3">
                    <div className="flex justify-between items-center mb-3">
                      <span className="font-semibold">Total:</span>
                      <span className="font-bold text-green-600">${getTotalPrice().toFixed(2)}</span>
                    </div>
                    <Button className="w-full bg-green-600 hover:bg-green-700">
                      Checkout
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
};

export default ShoppingCartButton;
