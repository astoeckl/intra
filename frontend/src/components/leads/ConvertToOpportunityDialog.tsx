import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { toast } from 'sonner'
import { TrendingUp, DollarSign, Calendar } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useConvertLeadToOpportunity } from '@/hooks/use-opportunities'
import type { LeadListItem } from '@/lib/types'

const formSchema = z.object({
  name: z.string().min(1, 'Name ist erforderlich').max(255),
  expected_value: z.preprocess(
    (val) => (val === '' ? undefined : Number(val)),
    z.number().min(0, 'Wert muss positiv sein').optional()
  ),
  expected_close_date: z.string().optional(),
  notes: z.string().optional(),
})

type FormValues = z.infer<typeof formSchema>

interface ConvertToOpportunityDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  lead: LeadListItem | null
}

export function ConvertToOpportunityDialog({
  open,
  onOpenChange,
  lead,
}: ConvertToOpportunityDialogProps) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      expected_value: undefined,
      expected_close_date: '',
      notes: '',
    },
  })

  const convertLead = useConvertLeadToOpportunity()

  useEffect(() => {
    if (lead && open) {
      // Generate default opportunity name from contact/company
      const defaultName = lead.company_name
        ? `${lead.company_name} - Opportunity`
        : `${lead.contact_name} - Opportunity`
      
      form.reset({
        name: defaultName,
        expected_value: undefined,
        expected_close_date: '',
        notes: '',
      })
    }
  }, [lead, open, form])

  const onSubmit = async (values: FormValues) => {
    if (!lead) return

    try {
      await convertLead.mutateAsync({
        leadId: lead.id,
        data: {
          name: values.name,
          expected_value: values.expected_value,
          expected_close_date: values.expected_close_date || undefined,
          notes: values.notes,
        },
      })
      toast.success('Lead erfolgreich in Opportunity konvertiert')
      onOpenChange(false)
    } catch {
      toast.error('Fehler beim Konvertieren des Leads')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-emerald-500" />
            Lead in Opportunity konvertieren
          </DialogTitle>
          <DialogDescription>
            Erstellen Sie eine neue Opportunity aus dem Lead{' '}
            <span className="font-medium">{lead?.contact_name}</span>
            {lead?.company_name && (
              <> von <span className="font-medium">{lead.company_name}</span></>
            )}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Opportunity Name *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="z.B. Website Redesign Projekt"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="expected_value"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-1">
                      <DollarSign className="h-3.5 w-3.5" />
                      Erwarteter Wert (EUR)
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="0"
                        step="100"
                        placeholder="10000"
                        {...field}
                        value={field.value ?? ''}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="expected_close_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-1">
                      <Calendar className="h-3.5 w-3.5" />
                      Erwarteter Abschluss
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="date"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notizen</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Zusätzliche Informationen zur Opportunity..."
                      rows={3}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Abbrechen
              </Button>
              <Button
                type="submit"
                disabled={convertLead.isPending}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                {convertLead.isPending ? 'Konvertiere...' : 'Konvertieren'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
