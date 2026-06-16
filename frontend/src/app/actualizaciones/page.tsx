'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Typography, Button, CircularProgress, Fade,
  Alert, Accordion, AccordionSummary, AccordionDetails, Chip, alpha,
} from '@mui/material'
import { SystemUpdate, ExpandMore, NewReleases, CheckCircle } from '@mui/icons-material'
import api from '@/lib/api'
import { useTheme } from '@mui/material'

export default function ActualizacionesPage() {
  const theme = useTheme()
  const [releases, setReleases] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [currentVersion, setCurrentVersion] = useState('')
  const [expanded, setExpanded] = useState<string | false>(false)

  useEffect(() => {
    api.get('/actualizaciones/').then((r) => {
      setReleases(r.data.releases || [])
      if (r.data.releases?.length > 0) setCurrentVersion(r.data.releases[0].tag_name)
    }).finally(() => setLoading(false))
  }, [])

  const handleAccordion = (panel: string) => (_: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false)
  }

  return (
    <Fade in timeout={300}>
      <Box>
        <Box display="flex" alignItems="center" gap={1.5} mb={3}>
          <Box sx={{ width: 40, height: 40, borderRadius: 2, display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`, color: '#fff' }}>
            <SystemUpdate fontSize="small" />
          </Box>
          <Box>
            <Typography variant="h4" fontWeight={700}>Verificar Actualizaciones</Typography>
            <Typography variant="caption" color="text.secondary">Releases de GitHub</Typography>
          </Box>
        </Box>

        {loading ? (
          <Box textAlign="center" py={6}><CircularProgress /></Box>
        ) : (
          <>
            {/* Status */}
            <Card sx={{ borderRadius: 3, mb: 2, bgcolor: releases.length > 0 ? alpha(theme.palette.success.main, 0.05) : alpha(theme.palette.info.main, 0.05) }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2, py: 2 }}>
                {releases.length > 0 ? <CheckCircle color="success" /> : <NewReleases color="info" />}
                <Box>
                  <Typography fontWeight={600}>
                    {releases.length > 0 ? '¡Estás actualizado!' : 'No se encontraron releases'}
                  </Typography>
                  {currentVersion && (
                    <Typography variant="caption" color="text.secondary">
                      Última versión: <strong>{currentVersion}</strong>
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>

            {/* Releases accordion */}
            {releases.length > 0 && (
              <>
                <Typography variant="h6" fontWeight={600} mb={1.5}>Detalles de las Releases:</Typography>
                {releases.map((release, i) => (
                  <Accordion
                    key={release.tag_name}
                    expanded={expanded === `panel${i}`}
                    onChange={handleAccordion(`panel${i}`)}
                    sx={{
                      borderRadius: '12px !important', mb: 1,
                      boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                      '&:before': { display: 'none' },
                      '&.Mui-expanded': { margin: '0 0 8px 0' },
                    }}
                  >
                    <AccordionSummary expandIcon={<ExpandMore />}
                      sx={{ borderRadius: 2, '&.Mui-expanded': { borderBottom: 1, borderColor: 'divider' } }}>
                      <Box display="flex" alignItems="center" gap={1.5}>
                        <Chip label={`v${release.tag_name}`} size="small" color={i === 0 ? 'primary' : 'default'} />
                        <Box>
                          <Typography fontWeight={600}>{release.name || release.tag_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            Publicado el: {new Date(release.published_at).toLocaleDateString('es-CL', { year: 'numeric', month: 'long', day: 'numeric' })}
                          </Typography>
                        </Box>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails sx={{ py: 2 }}>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
                        {release.body || 'Sin descripción'}
                      </Typography>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </>
            )}
          </>
        )}
      </Box>
    </Fade>
  )
}
