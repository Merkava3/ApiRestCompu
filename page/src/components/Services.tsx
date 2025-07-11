
import { Wrench, Shield, HardDrive, Laptop, Monitor, Camera } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const Services = () => {
  const repairServices = [
    {
      icon: Laptop,
      title: "Laptop Repair",
      description: "Screen replacement, keyboard repair, battery issues, and performance optimization",
      features: ["Screen Replacement", "Keyboard Repair", "Battery Replacement", "Performance Tuning"]
    },
    {
      icon: Monitor,
      title: "Desktop Computer Repair",
      description: "Hardware diagnostics, component replacement, virus removal, and system upgrades",
      features: ["Hardware Diagnostics", "Component Replacement", "Virus Removal", "System Upgrades"]
    },
    {
      icon: HardDrive,
      title: "Data Recovery",
      description: "Professional data recovery services for damaged or corrupted storage devices",
      features: ["Hard Drive Recovery", "SSD Recovery", "File Restoration", "Backup Solutions"]
    }
  ];

  const installationServices = [
    {
      icon: Shield,
      title: "Security Camera Installation",
      description: "Complete security camera system setup and configuration",
      features: ["Camera Mounting", "Network Setup", "Mobile App Config", "24/7 Monitoring"]
    },
    {
      icon: Camera,
      title: "Surveillance Systems",
      description: "Advanced surveillance solutions for homes and businesses",
      features: ["IP Cameras", "DVR/NVR Setup", "Remote Access", "Motion Detection"]
    },
    {
      icon: Wrench,
      title: "Network Installation",
      description: "Professional network setup and optimization services",
      features: ["WiFi Setup", "Cable Management", "Router Config", "Network Security"]
    }
  ];

  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-slate-800 mb-4">Our Services</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Professional technology repair and installation services you can trust
          </p>
        </div>

        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-slate-800 mb-12">Repair Services</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {repairServices.map((service, index) => (
              <Card key={index} className="hover:shadow-xl transition-shadow duration-300 border-green-200">
                <CardHeader className="text-center">
                  <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <service.icon className="w-8 h-8 text-green-600" />
                  </div>
                  <CardTitle className="text-xl text-slate-800">{service.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4">{service.description}</p>
                  <ul className="space-y-2">
                    {service.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center text-sm text-gray-700">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-3xl font-bold text-center text-slate-800 mb-12">Installation Services</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {installationServices.map((service, index) => (
              <Card key={index} className="hover:shadow-xl transition-shadow duration-300 border-green-200">
                <CardHeader className="text-center">
                  <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                    <service.icon className="w-8 h-8 text-green-600" />
                  </div>
                  <CardTitle className="text-xl text-slate-800">{service.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4">{service.description}</p>
                  <ul className="space-y-2">
                    {service.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center text-sm text-gray-700">
                        <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Services;
