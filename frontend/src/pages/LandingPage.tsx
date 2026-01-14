/**
 * Landing Page Template for Lead Generation
 * 
 * This is a standalone page that can be deployed separately or
 * integrated into marketing campaigns.
 * 
 * Usage: /landing/:campaignId
 */
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { CheckCircle2, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { api } from '@/lib/api'

const leadSchema = z.object({
  first_name: z.string().min(1, 'Vorname ist erforderlich'),
  last_name: z.string().min(1, 'Nachname ist erforderlich'),
  email: z.string().email('Ungültige E-Mail-Adresse'),
  phone: z.string().optional(),
  company_name: z.string().optional(),
})

type LeadFormData = z.infer<typeof leadSchema>

interface LandingPageProps {
  campaignId?: number
}

export default function LandingPage({ campaignId }: LandingPageProps) {
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Get UTM parameters from URL
  const params = new URLSearchParams(window.location.search)
  const utm_source = params.get('utm_source') || undefined
  const utm_medium = params.get('utm_medium') || undefined
  const utm_campaign = params.get('utm_campaign') || undefined

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LeadFormData>({
    resolver: zodResolver(leadSchema),
  })

  const onSubmit = async (data: LeadFormData) => {
    setIsSubmitting(true)
    setError(null)

    try {
      await api.post('/public/leads', {
        ...data,
        campaign_id: campaignId,
        utm_source,
        utm_medium,
        utm_campaign,
      })
      setIsSubmitted(true)
    } catch (e) {
      setError('Es ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-md text-center animate-fade-in">
          <CardContent className="pt-10 pb-10">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-accent/10">
              <CheckCircle2 className="h-8 w-8 text-accent" />
            </div>
            <h2 className="text-2xl font-bold font-display mb-2">Vielen Dank!</h2>
            <p className="text-muted-foreground">
              Wir haben Ihre Anfrage erhalten und werden uns in Kürze bei Ihnen melden.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md animate-fade-in">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-display">
            Kostenlose Beratung anfordern
          </CardTitle>
          <CardDescription>
            Füllen Sie das Formular aus und wir melden uns bei Ihnen
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">Vorname *</Label>
                <Input
                  id="first_name"
                  {...register('first_name')}
                  className={errors.first_name ? 'border-destructive' : ''}
                />
                {errors.first_name && (
                  <p className="text-xs text-destructive">{errors.first_name.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Nachname *</Label>
                <Input
                  id="last_name"
                  {...register('last_name')}
                  className={errors.last_name ? 'border-destructive' : ''}
                />
                {errors.last_name && (
                  <p className="text-xs text-destructive">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">E-Mail *</Label>
              <Input
                id="email"
                type="email"
                {...register('email')}
                className={errors.email ? 'border-destructive' : ''}
              />
              {errors.email && (
                <p className="text-xs text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Telefon</Label>
              <Input id="phone" {...register('phone')} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="company_name">Firma</Label>
              <Input id="company_name" {...register('company_name')} />
            </div>

            {error && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Wird gesendet...
                </>
              ) : (
                'Jetzt anfordern'
              )}
            </Button>

            <p className="text-xs text-center text-muted-foreground">
              Mit dem Absenden stimmen Sie unserer Datenschutzerklärung zu.
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
