
import { Phone, Mail, MapPin, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const Contact = () => {
  return (
    <section className="py-20 px-4 bg-slate-900 text-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Get In Touch</h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Ready to fix your tech or upgrade your setup? Contact us today for expert service.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div>
            <h3 className="text-2xl font-bold mb-8">Contact Information</h3>
            
            <div className="space-y-6 mb-8">
              <div className="flex items-center">
                <div className="bg-green-600 p-3 rounded-full mr-4">
                  <Phone className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-semibold">Phone</h4>
                  <p className="text-gray-300">(555) 123-4567</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <div className="bg-green-600 p-3 rounded-full mr-4">
                  <Mail className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-semibold">Email</h4>
                  <p className="text-gray-300">info@tecnoxpress.com</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <div className="bg-green-600 p-3 rounded-full mr-4">
                  <MapPin className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-semibold">Address</h4>
                  <p className="text-gray-300">123 Tech Street, Digital City, TC 12345</p>
                </div>
              </div>
              
              <div className="flex items-center">
                <div className="bg-green-600 p-3 rounded-full mr-4">
                  <Clock className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="font-semibold">Business Hours</h4>
                  <p className="text-gray-300">Mon-Fri: 9AM-6PM | Sat: 10AM-4PM</p>
                </div>
              </div>
            </div>

            <Card className="bg-slate-800 border-green-500/30">
              <CardHeader>
                <CardTitle className="text-white">Emergency Repair Service</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 mb-4">
                  Need urgent repair? We offer emergency service for critical business systems.
                </p>
                <Button className="bg-red-600 hover:bg-red-700">
                  Call Emergency Line: (555) 911-TECH
                </Button>
              </CardContent>
            </Card>
          </div>

          <div>
            <Card className="bg-slate-800 border-green-500/30 h-full">
              <CardHeader>
                <CardTitle className="text-white">Find Us</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="w-full h-96 bg-slate-700 rounded-b-lg overflow-hidden">
                  <iframe
                    src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3024.123456789!2d-74.00123456789!3d40.71234567890!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNDDCsDQyJzQ0LjQiTiA3NMKwMDAnMDQuNCJX!5e0!3m2!1sen!2sus!4v1234567890123!5m2!1sen!2sus"
                    width="100%"
                    height="100%"
                    style={{ border: 0 }}
                    allowFullScreen
                    loading="lazy"
                    referrerPolicy="no-referrer-when-downgrade"
                    title="TecnoXpress Location"
                  ></iframe>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Contact;
