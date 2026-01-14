import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useCreateOpportunity, useUpdateOpportunity, useCloseOpportunity } from '@/hooks/use-opportunities'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { OpportunityListItem, OpportunityCreate, OpportunityStage } from '@/lib/types'
import { STAGE_LABELS } from '@/lib/types'
import { toast } from 'sonner'

interface OpportunityDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  opportunity: OpportunityListItem | null
}

interface FormData {
  name: string
  stage: OpportunityStage
  expected_value: string
  probability: string
  expected_close_date: string
  notes: string
}

export function OpportunityDialog({ open, onOpenChange, opportunity }: OpportunityDialogProps) {
  const createOpportunity = useCreateOpportunity()
  const updateOpportunity = useUpdateOpportunity()
  const closeOpportunity = useCloseOpportunity()

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    defaultValues: {
      name: '',
      stage: 'qualification',
      expected_value: '',
      probability: '10',
      expected_close_date: '',
      notes: '',
    },
  })

  const currentStage = watch('stage')

  useEffect(() => {
    if (opportunity) {
      reset({
        name: opportunity.name,
        stage: opportunity.stage,
        expected_value: opportunity.expected_value?.toString() || '',
        probability: opportunity.probability.toString(),
        expected_close_date: opportunity.expected_close_date || '',
        notes: '',
      })
    } else {
      reset({
        name: '',
        stage: 'qualification',
        expected_value: '',
        probability: '10',
        expected_close_date: '',
        notes: '',
      })
    }
  }, [opportunity, reset])

  const onSubmit = async (data: FormData) => {
    try {
      const payload: OpportunityCreate = {
        name: data.name,
        stage: data.stage,
        expected_value: data.expected_value ? parseFloat(data.expected_value) : undefined,
        probability: parseInt(data.probability),
        expected_close_date: data.expected_close_date || undefined,
        notes: data.notes || undefined,
      }

      if (opportunity) {
        await updateOpportunity.mutateAsync({
          id: opportunity.id,
          data: payload,
        })
        toast.success('Opportunity aktualisiert')
      } else {
        await createOpportunity.mutateAsync(payload)
        toast.success('Opportunity erstellt')
      }
      onOpenChange(false)
    } catch {
      toast.error('Fehler beim Speichern')
    }
  }

  const handleClose = async (won: boolean) => {
    if (!opportunity) return
    
    const reason = prompt(won ? 'Grund fuer Gewinn:' : 'Grund fuer Verlust:')
    
    try {
      await closeOpportunity.mutateAsync({
        id: opportunity.id,
        data: {
          won,
          close_reason: reason || undefined,
        },
      })
      toast.success(won ? 'Opportunity als gewonnen markiert' : 'Opportunity als verloren markiert')
      onOpenChange(false)
    } catch {
      toast.error('Fehler beim Schliessen')
    }
  }

  const isEditing = !!opportunity
  const isClosed = opportunity?.stage === 'closed_won' || opportunity?.stage === 'closed_lost'

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? 'Opportunity bearbeiten' : 'Neue Opportunity'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              {...register('name', { required: 'Name ist erforderlich' })}
              placeholder="z.B. Website Redesign Projekt"
              disabled={isClosed}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="stage">Stage</Label>
              <Select
                value={currentStage}
                onValueChange={(value) => setValue('stage', value as OpportunityStage)}
                disabled={isClosed}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(STAGE_LABELS).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="probability">Wahrscheinlichkeit (%)</Label>
              <Input
                id="probability"
                type="number"
                min="0"
                max="100"
                {...register('probability')}
                disabled={isClosed}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="expected_value">Erwarteter Wert (EUR)</Label>
              <Input
                id="expected_value"
                type="number"
                min="0"
                step="100"
                {...register('expected_value')}
                placeholder="10000"
                disabled={isClosed}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="expected_close_date">Erwarteter Abschluss</Label>
              <Input
                id="expected_close_date"
                type="date"
                {...register('expected_close_date')}
                disabled={isClosed}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notizen</Label>
            <Textarea
              id="notes"
              {...register('notes')}
              placeholder="Zusaetzliche Informationen..."
              rows={3}
              disabled={isClosed}
            />
          </div>

          <DialogFooter className="gap-2">
            {isEditing && !isClosed && (
              <>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleClose(false)}
                  className="text-red-600 hover:text-red-700"
                >
                  Als verloren markieren
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleClose(true)}
                  className="text-emerald-600 hover:text-emerald-700"
                >
                  Als gewonnen markieren
                </Button>
              </>
            )}
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Abbrechen
            </Button>
            {!isClosed && (
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Speichern...' : 'Speichern'}
              </Button>
            )}
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}