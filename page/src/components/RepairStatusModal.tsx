
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { jsPDF } from "jspdf";

interface RepairInfo {
  cod: string;
  nombreCliente: string;
  direccion: string;
  telefono: string;
  tipoEquipo: string;
}

interface RepairStatusModalProps {
  open: boolean;
  onClose: () => void;
  repairInfo: RepairInfo | null;
  notFound?: boolean;
  searchCode?: string;
}

export default function RepairStatusModal({
  open,
  onClose,
  repairInfo,
  notFound = false,
  searchCode = "",
}: RepairStatusModalProps) {
  if (!open) return null;

  const handleCreatePdf = () => {
    if (!repairInfo) return;
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("Información de Reparación", 10, 12);
    doc.setFontSize(12);
    doc.text(`Código: ${repairInfo.cod}`, 10, 25);
    doc.text(`Nombre cliente: ${repairInfo.nombreCliente}`, 10, 35);
    doc.text(`Dirección: ${repairInfo.direccion}`, 10, 45);
    doc.text(`Teléfono: ${repairInfo.telefono}`, 10, 55);
    doc.text(`Tipo equipo: ${repairInfo.tipoEquipo}`, 10, 65);
    doc.save(`reparacion_${repairInfo.cod}.pdf`);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-xs">
        <DialogHeader>
          <DialogTitle>Estado de Reparación</DialogTitle>
          {!notFound && repairInfo ? (
            <DialogDescription>
              Detalles para el código <span className="font-bold">{repairInfo.cod}</span>
            </DialogDescription>
          ) : (
            <DialogDescription>
              No se encontró información para el código <span className="font-bold">{searchCode}</span>
            </DialogDescription>
          )}
        </DialogHeader>
        {repairInfo && !notFound ? (
          <div className="space-y-1 text-base py-2">
            <div>
              <span className="font-medium">Nombre cliente:</span> {repairInfo.nombreCliente}
            </div>
            <div>
              <span className="font-medium">Dirección:</span> {repairInfo.direccion}
            </div>
            <div>
              <span className="font-medium">Teléfono:</span> {repairInfo.telefono}
            </div>
            <div>
              <span className="font-medium">Tipo equipo:</span> {repairInfo.tipoEquipo}
            </div>
          </div>
        ) : (
          <div className="py-4 text-center text-sm text-red-500">No hay datos para mostrar.</div>
        )}
        <DialogFooter>
          {!notFound && repairInfo && (
            <Button onClick={handleCreatePdf}>Crear PDF</Button>
          )}
          <Button variant="outline" onClick={onClose}>
            Cerrar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
