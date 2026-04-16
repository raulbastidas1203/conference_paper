# Workflow: Pre-Writing Research Phase (Phase 0)

Este workflow cubre todo el trabajo previo a la escritura del manuscript: desde la definición
del problema hasta tener un plan de experimentos aprobado, un registro de claims y un
blueprint de figuras/tablas. Cuando este workflow termina, estás listo para ejecutar
experimentos y luego entrar directo a la fase de escritura.

---

## ¿Cuándo usar este workflow?

- Al iniciar un paper nuevo, antes de escribir cualquier sección
- Cuando tienes una idea de contribución pero aún no tienes resultados
- Cuando tienes resultados preliminares y quieres estructurar los experimentos restantes
- Cuando necesitas validar que tu diseño experimental soportará las claims que planeas hacer

---

## Entradas requeridas (antes de empezar)

- [ ] Idea de contribución: ¿qué problema resuelve tu método, y en qué es diferente de lo existente?
- [ ] Venue objetivo: ¿a dónde vas a enviar? (ICRA, CoRL, RSS, RA-L, etc.)
- [ ] Deadline de submission
- [ ] Recursos disponibles: ¿robot real? ¿cuántas horas de cómputo? ¿colección de demos?

---

## Fase 0.1 — Definición del problema y la contribución

### Objetivo
Formular la contribución de forma específica y falsificable antes de hacer cualquier otra cosa.

### Pasos

1. Responde estas preguntas (escríbelas en `templates/paper-outline.md`):
   - ¿Cuál es el problema que resuelves? (una sola oración)
   - ¿Por qué el estado del arte no lo resuelve? (gap específico)
   - ¿Cuál es tu enfoque? (descripción técnica de 2–3 oraciones)
   - ¿Cuál es la evidencia que demostrará que funciona? (resultado cuantitativo esperado)
   - ¿Cuándo sería tu método peor que el estado del arte? (honestidad sobre limitaciones)

2. Escribe 2–4 contribuciones específicas y verificables. Cada una debe:
   - Ser **falsificable** ("nuestro método logra ≥X% SR en benchmark Y")
   - Ser **verificable** en el paper (una tabla, una figura, un teorema)
   - No ser genérica ("proponemos un enfoque novedoso" no cuenta)

3. Identifica el venue objetivo y confirma que la contribución es relevante para ese venue.
   Ver `.claude/references/venue-profiles.md` para scope y expectativas.

### Señal de completitud
- La contribución está escrita en `templates/paper-outline.md`
- Puedes formularla como: "Presentamos [método] que [qué hace] y demostramos [evidencia cuantitativa] en [benchmark/task]"
- Si no puedes llenarlo, el problema no está bien definido todavía

---

## Fase 0.2 — Literatura relevante y baselines

### Objetivo
Identificar los papers que serán comparados, los benchmarks que serán usados, y los gaps
que posicionan tu contribución.

### Pasos

1. **Búsqueda primaria:**
   ```
   /search-lit <tema principal>
   /search-lit <método específico>
   /search-lit <benchmark o task>
   ```
   Repite con 2–3 queries distintas. Ver `workflows/lit-review.md` para protocolo completo.

2. **Clasificación:**
   - **Central:** misma tarea, mismo dominio, competidores directos → leer full-text
   - **Related:** aspecto relevante → leer abstract
   - **Marginal:** keywords compartidos → listar sin leer

3. **Identificación de baselines:**
   Para cada baseline candidato en tus tablas:
   - ¿Existe y es citable? (Librarian verifica)
   - ¿Es el más fuerte disponible en su familia? (no comparar contra versiones obsoletas)
   - ¿Usa el mismo input modality que tu método?
   - ¿Tiene implementación pública para replicar?

4. **Identificación de benchmarks:**
   Ver `.claude/references/benchmark-notes.md`. Para el venue elegido, confirmar:
   - ¿Usan este benchmark papers recientes en ese venue?
   - ¿El benchmark tiene suficiente diversidad de tareas para tu claim?
   - ¿Requiere el venue validación en robot real?

### Papers a recuperar (NEED-PDF)
Al final de cada `/search-lit`, el Librarian listará papers que requieren acceso pago.
Estos van a `references/tracker.md` bajo "Papers to retrieve". Recuperarlos con acceso
universitario y colocarlos en `/papers/`.

### Señal de completitud
- ≥5 papers Central verificados en `references/tracker.md`
- Al menos 1 paper Central de ICRA/IROS/CoRL/RSS/RA-L/T-RO
- Baselines candidatos identificados y verificados (o marcados para verificar)
- Benchmark(s) seleccionados y justificados

---

## Fase 0.3 — Diseño de experimentos

### Objetivo
Transformar la lista de contribuciones en un plan de experimentos concreto, aprobado
por ti antes de ejecutar ningún experimento.

### Pasos

1. **Ejecutar el skill:**
   ```
   /plan-experiments --venue <venue>
   ```

2. **Revisar el output** en `outputs/experiment-plan-<date>.md`:
   - ¿Cada contribución tiene al menos un experimento que puede confirmarla o refutarla?
   - ¿Los baselines son justos (mismo input modality, misma información)?
   - ¿El N de trials cumple el mínimo del domain (≥20 manipulation, ≥100 navigation)?
   - ¿El ablation schedule cubre todos los componentes que describes como importantes?
   - ¿El scope de sim vs. real está explícito (INV-16)?

3. **Responder las preguntas abiertas** listadas al final del plan (recursos, robot real, demos disponibles).

4. **Aprobar el plan:** cambiar el campo `Status: DRAFT` → `Status: APPROVED` en el archivo.
   Este cambio es tu compromiso: los experimentos que ejecutes deben seguir este protocolo.

5. **Recuperar NEED-PDF papers** listados en el plan antes de empezar experimentos.

### Señal de completitud
- `outputs/experiment-plan-<date>.md` tiene `Status: APPROVED`
- Todas las preguntas abiertas respondidas
- Ningún NEED-PDF crítico pendiente (o usuario confirmó que los conseguirá)

---

## Fase 0.4 — Registro de claims (Stage A)

### Objetivo
Construir el mapa de claims → evidencia antes de tener resultados, para identificar
claims sin experimento diseñado antes de que sea tarde corregirlos.

### Pasos

1. **Ejecutar el skill:**
   ```
   /track-claims --stage A
   ```

2. **Revisar el output** en `outputs/claim-evidence-map-<date>.md`:
   - ¿Hay claims con status MISSING? (bloqueantes — necesitan experimento o eliminarse)
   - ¿Hay claims SPECULATIVE? (requieren búsqueda bibliográfica para INV-17)
   - ¿Todos los claims de contribución tienen una hypothesis en el experiment plan?

3. **Resolver issues BLOCKING antes de ejecutar experimentos:**
   - Claims MISSING: agregar fila al experiment plan OR reformular la contribución
   - Claims SPECULATIVE: ejecutar `/search-lit` adicional y verificar con Librarian

### Señal de completitud
- Ningún claim con status MISSING (todos los claims tienen experimento diseñado)
- Claims SPECULATIVE enrutados a búsqueda bibliográfica
- El mapa está guardado como referencia para Stage B durante el drafting

---

## Fase 0.5 — Blueprint de figuras y tablas

### Objetivo
Diseñar el conjunto completo de figuras y tablas antes de escribir. Esto establece
la narrativa visual y asegura que cada claim tenga un artifact visual asociado.

### Pasos

1. **Ejecutar el skill:**
   ```
   /plan-figures --venue <venue>
   ```

2. **Revisar el output** en `outputs/figures-plan-<date>.md`:
   - ¿Cada claim del mapa Stage A tiene una tabla o figura asignada?
   - ¿Las tablas siguen INV-1/2/3 (booktabs, mean±std, N trials)?
   - ¿Las figuras seguirán INV-6/7/19 (grayscale, autocontained, LaTeX labels)?
   - ¿El ablation está en una tabla separada (INV-12)?
   - ¿El número total de figuras/tablas cabe en el page limit del venue?

3. **Ajustar el blueprint** según los constraints del venue (doble columna, página límite).

### Señal de completitud
- Cada claim → artifact visual mapeado
- Blueprint guardado en `outputs/figures-plan-<date>.md`
- Sin conflictos con page limit del venue

---

## Resumen del Phase 0

```
0.1 DEFINICIÓN
    Output: templates/paper-outline.md (contribution + venue + problem statement)
    Gate: contribución falsificable y específica

0.2 LITERATURA Y BASELINES
    Run: /search-lit <topic> (2–3 queries)
    Output: references/tracker.md actualizado, NEED-PDF identificados
    Gate: ≥5 Central papers verified; baselines candidatos identificados

0.3 DISEÑO DE EXPERIMENTOS
    Run: /plan-experiments --venue <venue>
    Output: outputs/experiment-plan-<date>.md (APPROVED)
    Gate: todas las contribuciones tienen experimento; N cumple mínimos; ablation completo

0.4 REGISTRO DE CLAIMS (Stage A)
    Run: /track-claims --stage A
    Output: outputs/claim-evidence-map-<date>.md
    Gate: no claims MISSING; SPECULATIVE enrutados

0.5 BLUEPRINT DE FIGURAS
    Run: /plan-figures --venue <venue>
    Output: outputs/figures-plan-<date>.md
    Gate: todos los claims tienen artifact visual; cabe en page limit
```

---

## Transición a Phase 1

Cuando todos los gates de Phase 0 están verdes:

1. Ejecutar los experimentos según el plan aprobado
2. Llenar los resultados en las tablas del blueprint (incluso antes de escribir el texto)
3. Ejecutar `/track-claims --stage B` después de cada sección drafted para mantener el mapa actualizado
4. Continuar con `workflows/new-paper.md` Phase 1 (Scoping → ya hecho) → Phase 2 (Discovery, completado) → Phase 3 (Synthesis: `/related-work`) → Phase 4 (Drafting)

El orden de drafting recomendado (de `workflows/new-paper.md`) es:
Methodology → Experiments → Results → Related Work → Introduction → Abstract → Conclusion

---

## Señales de que Phase 0 está incompleto

Si alguno de estos sigue siendo verdad, NO estás listo para ejecutar experimentos:

- [ ] Las contribuciones son genéricas ("mejoramos el estado del arte") sin métrica específica
- [ ] Hay claims en el plan sin experimento diseñado
- [ ] No sabes qué baselines vas a comparar
- [ ] No sabes cuántos trials vas a correr
- [ ] El scope sim-only vs. real-robot no está definido
- [ ] Los NEED-PDF de baselines centrales siguen sin recuperar
