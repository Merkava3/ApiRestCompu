
import { useState } from 'react';
import { Search, Computer, Shield, Wrench } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import RepairStatusModal from './RepairStatusModal';

const MOCK_ORDERS = [
  {
    cod: "123456789",
    nombreCliente: "Homero simpson",
    direccion: "calle falsa 123",
    telefono: "678-920",
    tipoEquipo: "portatil",
  },
  // Puedes agregar más objetos aquí si necesitas más pruebas
];

const Hero = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<null | typeof MOCK_ORDERS[0]>(null);
  const [orderNotFound, setOrderNotFound] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const order = MOCK_ORDERS.find(o => o.cod === searchQuery.trim());
    if (order) {
      setSelectedOrder(order);
      setOrderNotFound(false);
      setModalOpen(true);
    } else {
      setSelectedOrder(null);
      setOrderNotFound(true);
      setModalOpen(true);
    }
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedOrder(null);
    setOrderNotFound(false);
  };

  return (
    <section className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white py-20 px-4">
      <div className="absolute inset-0 bg-black/20"></div>
      <div className="relative max-w-6xl mx-auto text-center">
        <div className="flex justify-center mb-6">
          <div className="relative">
            <img 
              src="/imagen/308c7716-f13e-436c-9f9c-d62dc9d92e93.png" 
              alt="TecnoXpress Logo" 
              className="w-32 h-32 object-contain"
            />
          </div>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-green-300 to-green-500 bg-clip-text text-transparent">
          TecnoXpress
        </h1>
        
        <p className="text-xl md:text-2xl mb-8 text-gray-100 max-w-3xl mx-auto">
          Expert Computer & Electronics Repair | Security Camera Installation | Technology Sales
        </p>
        
        <form onSubmit={handleSearch} className="max-w-2xl mx-auto mb-12">
          <div className="relative flex">
            <Input
              type="text"
              placeholder="Ingresa tu código de reparación para ver el estado..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 h-14 text-lg pl-6 pr-14 bg-white/90 text-gray-800 border-0 rounded-l-full focus:ring-2 focus:ring-green-400"
              autoFocus
            />
            <Button 
              type="submit"
              className="h-14 px-8 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 border-0 rounded-r-full"
            >
              <Search className="w-5 h-5" />
            </Button>
          </div>
        </form>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-green-500/30">
            <Wrench className="w-8 h-8 text-green-400 mb-3 mx-auto" />
            <h3 className="text-lg font-semibold mb-2">Expert Repairs</h3>
            <p className="text-gray-100">Desktop, laptop, and electronics repair by certified technicians</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-green-500/30">
            <Shield className="w-8 h-8 text-green-400 mb-3 mx-auto" />
            <h3 className="text-lg font-semibold mb-2">Security Installation</h3>
            <p className="text-gray-100">Professional security camera installation and setup</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-green-500/30">
            <Computer className="w-8 h-8 text-green-400 mb-3 mx-auto" />
            <h3 className="text-lg font-semibold mb-2">Tech Products</h3>
            <p className="text-gray-100">Quality keyboards, mice, webcams, and accessories</p>
          </div>
        </div>
      </div>
      <RepairStatusModal
        open={modalOpen}
        onClose={handleCloseModal}
        repairInfo={selectedOrder}
        notFound={orderNotFound}
        searchCode={searchQuery}
      />
    </section>
  );
};

export default Hero;
