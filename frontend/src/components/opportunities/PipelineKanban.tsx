import { useState, useMemo } from 'react'
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { GripVertical, Building2, User, Calendar, DollarSign } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { useOpportunities, useUpdateOpportunity } from '@/hooks/use-opportunities'
import type { OpportunityListItem, OpportunityStage } from '@/lib/types'
import { STAGE_LABELS, STAGE_COLORS } from '@/lib/types'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { toast } from 'sonner'

// Active pipeline stages (excluding closed)
const PIPELINE_STAGES: OpportunityStage[] = [
  'qualification',
  'discovery',
  'proposal',
  'negotiation',
]

function formatCurrency(value: number | undefined): string {
  if (value === undefined || value === null) return '-'
  return new Intl.NumberFormat('de-AT', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

interface OpportunityCardProps {
  opportunity: OpportunityListItem
  onClick?: () => void
  isDragging?: boolean
}

function OpportunityCard({ opportunity, onClick, isDragging }: OpportunityCardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border bg-card p-3 shadow-sm transition-all cursor-pointer hover:shadow-md',
        isDragging && 'opacity-50 rotate-2 scale-105 shadow-lg'
      )}
      onClick={onClick}
    >
      <div className="flex items-start gap-2">
        <GripVertical className="h-4 w-4 text-muted-foreground/50 mt-0.5 shrink-0 cursor-grab" />
        <div className="flex-1 min-w-0 space-y-2">
          <p className="font-medium text-sm truncate">{opportunity.name}</p>
          
          {opportunity.expected_value && (
            <div className="flex items-center gap-1 text-emerald-600">
              <DollarSign className="h-3.5 w-3.5" />
              <span className="text-sm font-semibold">
                {formatCurrency(opportunity.expected_value)}
              </span>
            </div>
          )}

          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
            {opportunity.company_name && (
              <div className="flex items-center gap-1">
                <Building2 className="h-3 w-3" />
                <span className="truncate max-w-[100px]">{opportunity.company_name}</span>
              </div>
            )}
            {opportunity.contact_name && (
              <div className="flex items-center gap-1">
                <User className="h-3 w-3" />
                <span className="truncate max-w-[100px]">{opportunity.contact_name}</span>
              </div>
            )}
          </div>

          {opportunity.expected_close_date && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>
                {format(new Date(opportunity.expected_close_date), 'dd.MM.yyyy', { locale: de })}
              </span>
            </div>
          )}

          <div className="flex items-center justify-between">
            <Badge variant="outline" className="text-xs">
              {opportunity.probability}%
            </Badge>
          </div>
        </div>
      </div>
    </div>
  )
}

interface SortableOpportunityCardProps {
  opportunity: OpportunityListItem
  onClick?: () => void
}

function SortableOpportunityCard({ opportunity, onClick }: SortableOpportunityCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: opportunity.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <OpportunityCard
        opportunity={opportunity}
        onClick={onClick}
        isDragging={isDragging}
      />
    </div>
  )
}

interface StageColumnProps {
  stage: OpportunityStage
  opportunities: OpportunityListItem[]
  onCardClick?: (opportunity: OpportunityListItem) => void
}

function StageColumn({ stage, opportunities, onCardClick }: StageColumnProps) {
  const totalValue = useMemo(
    () => opportunities.reduce((sum, opp) => sum + (opp.expected_value || 0), 0),
    [opportunities]
  )

  return (
    <div className="flex flex-col min-w-[280px] max-w-[320px] bg-muted/30 rounded-lg">
      <div className={cn('rounded-t-lg px-3 py-2', STAGE_COLORS[stage])}>
        <div className="flex items-center justify-between text-white">
          <h3 className="font-semibold text-sm">{STAGE_LABELS[stage]}</h3>
          <Badge variant="secondary" className="bg-white/20 text-white hover:bg-white/30">
            {opportunities.length}
          </Badge>
        </div>
        <p className="text-white/80 text-xs mt-1">
          {formatCurrency(totalValue)}
        </p>
      </div>
      
      <div className="p-2 space-y-2 flex-1 min-h-[200px] max-h-[calc(100vh-400px)] overflow-y-auto">
        <SortableContext
          items={opportunities.map(o => o.id)}
          strategy={verticalListSortingStrategy}
        >
          {opportunities.map((opportunity) => (
            <SortableOpportunityCard
              key={opportunity.id}
              opportunity={opportunity}
              onClick={() => onCardClick?.(opportunity)}
            />
          ))}
        </SortableContext>
        
        {opportunities.length === 0 && (
          <div className="flex items-center justify-center h-20 text-muted-foreground text-sm border-2 border-dashed rounded-lg">
            Keine Opportunities
          </div>
        )}
      </div>
    </div>
  )
}

interface PipelineKanbanProps {
  onCardClick?: (opportunity: OpportunityListItem) => void
}

export function PipelineKanban({ onCardClick }: PipelineKanbanProps) {
  const [activeOpportunity, setActiveOpportunity] = useState<OpportunityListItem | null>(null)
  
  // Fetch all open opportunities (exclude closed ones)
  const { data, isLoading } = useOpportunities({
    page_size: 100, // Get all for kanban view
  })
  
  const updateOpportunity = useUpdateOpportunity()

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Minimum drag distance before activating
      },
    }),
    useSensor(KeyboardSensor)
  )

  // Group opportunities by stage
  const opportunitiesByStage = useMemo(() => {
    const grouped: Record<OpportunityStage, OpportunityListItem[]> = {
      qualification: [],
      discovery: [],
      proposal: [],
      negotiation: [],
      closed_won: [],
      closed_lost: [],
    }

    data?.items.forEach((opp) => {
      if (grouped[opp.stage]) {
        grouped[opp.stage].push(opp)
      }
    })

    return grouped
  }, [data?.items])

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event
    const opportunity = data?.items.find((o) => o.id === active.id)
    if (opportunity) {
      setActiveOpportunity(opportunity)
    }
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    setActiveOpportunity(null)

    if (!over) return

    // Find the opportunity being dragged
    const opportunity = data?.items.find((o) => o.id === active.id)
    if (!opportunity) return

    // Determine the target stage
    let targetStage: OpportunityStage | null = null

    // Check if dropped on a stage column
    if (PIPELINE_STAGES.includes(over.id as OpportunityStage)) {
      targetStage = over.id as OpportunityStage
    } else {
      // Find which stage the target opportunity belongs to
      const targetOpp = data?.items.find((o) => o.id === over.id)
      if (targetOpp) {
        targetStage = targetOpp.stage
      }
    }

    // If stage changed, update the opportunity
    if (targetStage && targetStage !== opportunity.stage) {
      updateOpportunity.mutate(
        { id: opportunity.id, data: { stage: targetStage } },
        {
          onSuccess: () => {
            toast.success(`"${opportunity.name}" nach ${STAGE_LABELS[targetStage!]} verschoben`)
          },
          onError: () => {
            toast.error('Fehler beim Verschieben der Opportunity')
          },
        }
      )
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {PIPELINE_STAGES.map((stage) => (
          <StageColumn
            key={stage}
            stage={stage}
            opportunities={opportunitiesByStage[stage]}
            onCardClick={onCardClick}
          />
        ))}
      </div>

      <DragOverlay>
        {activeOpportunity && (
          <OpportunityCard opportunity={activeOpportunity} isDragging />
        )}
      </DragOverlay>
    </DndContext>
  )
}
