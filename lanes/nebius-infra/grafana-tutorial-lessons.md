---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
---

# Lessons from Grafana's tutorials and 12.4 docs for vy-nebius-1's Grafana

Research by [Grafana tutorials lessons](bc-72a9c2b3-b631-5239-b0c5-47b877f5c431), 16:01Z, Sep 30. Finding: the tutorials are
thin for our setup. The alerting ones are UI click-throughs on TestData, and the provisioning one dates from Grafana 7. Most lessons
come from the 12.4 docs the tutorials link to. Companion: `gpu-monitoring-practice.md`.

## How our config compares (16:05Z)

**Already as recommended:**
- file provisioning with fixed uids, `allowUiUpdates: false` and `id: null`;
- the webhook contact point, `disableResolveMessage: false`;
- grouping by `alertname`;
- mute timings on a child policy, not the root, with `location: UTC`;
- `noDataState: OK` on the held-at-0 rule;
- W's `or vector(0)` guard;
- `timeInterval: 60s`;
- anonymous access off, and Grafana on 127.0.0.1 only.

**Differences worth fixing:**
- **Pending period:** our rules use `for: 15m` / `for: 10m` on instant values. The docs suggest putting the window in PromQL
  (`max_over_time(...[15m])`) with a short `for` and `keepFiringFor`. That is less fragile to one noisy sample; adopt it when
  adding `keep_firing_for`.
- **Datasource errors:** `DatasourceError` / `DatasourceNoData` should get an explicit route.
- **Links:** `root_url = http://localhost:3000/` makes the links in notes work through the tunnel.
- **Upgrades:** before Grafana 13, back up `grafana.db` with Grafana stopped. 13.0.0 was pulled, so go to 13.0.1 or later. 12.4
  gets patches until 24 May 2027.

## Tutorials read

- [Grafana fundamentals](https://grafana.com/tutorials/grafana-fundamentals/): a first Grafana-managed rule (query → Reduce →
  Threshold), a webhook contact point, linking a rule to a panel.
- [Provision dashboards and data sources](https://grafana.com/tutorials/provision-dashboards-and-data-sources/): the directory layout
  only. Its sample JSON is obsolete.
- Get started with Grafana Alerting:
  [1](https://grafana.com/tutorials/alerting-get-started/),
  [2 (multi-dimensional alerts, routing)](https://grafana.com/tutorials/alerting-get-started-pt2/),
  [3 (grouping)](https://grafana.com/tutorials/alerting-get-started-pt3/),
  [4 (templating)](https://grafana.com/tutorials/alerting-get-started-pt4/),
  [5 (dynamic labels)](https://grafana.com/tutorials/alerting-get-started-pt5/),
  [6 (linking alerts to panels)](https://grafana.com/tutorials/alerting-get-started-pt6/).
- [Run Grafana behind a reverse proxy](https://grafana.com/tutorials/run-grafana-behind-a-proxy/): relevant only if we add one, for
  example for SkyPilot's `/grafana` embedding.

## 1. Provisioning

- **Dashboards:** a fixed `uid`, `"id": null` and `allowUiUpdates: false`, so the file wins on every restart. Export with "Export
  for sharing externally" off. `updateIntervalSeconds` above 10.
  [Provisioning](https://grafana.com/docs/grafana/v12.4/administration/provisioning/).
- **Data source:** `uid`, `editable: false`, `prune: true`.
- **Alerting files:** keys are `groups`, `contactPoints`, `policies`, `muteTimes` and `templates`; uids are at most 40 characters
  from `[A-Za-z0-9_-]`.
  - Deletion is explicit (`deleteRules` and the like).
  - The policy tree is one resource, so our file overwrites all of it.
  - Provisioned resources can't be edited in the UI: change the file, then restart or `POST /api/admin/provisioning/alerting/reload`.
  - Draft rules in the UI and export them with "Modify export" rather than hand-writing `data.model`.
  - `$VAR` in provisioning files comes from the environment, so escape `$$labels` in contact-point settings.
  - [File provisioning](https://grafana.com/docs/grafana/v12.4/alerting/set-up/provision-alerting-resources/file-provisioning/).
- **Rule edits** reset a rule's instances to Normal and restart pending timers.

## 2. Alerting

- **Query shape:** instant queries. Put the window in PromQL and return every series; apply the threshold in Grafana, not PromQL,
  or "none idle" becomes NoData or MissingSeries.
  [Missing data](https://grafana.com/docs/grafana/v12.4/alerting/guides/missing-data/).
- **Math with an unlabelled side:** a value with no labels joins every series (`$A < 5 && $B > 0`). If any query returns nothing,
  the rule goes NoData.
  [Expressions](https://grafana.com/docs/grafana/v12.4/visualizations/panels-visualizations/query-transform-data/expression-queries/).
- **Datasource alerts:** `DatasourceNoData` / `DatasourceError` skip `for` and may miss label-based policies, so route them
  explicitly by `datasource_uid`.
  [No data and error](https://grafana.com/docs/grafana/v12.4/alerting/fundamentals/alert-rule-evaluation/nodata-and-error-states/).
- **Flapping:** `keepFiringFor`, or a recovery threshold (Threshold conditions only).
- **Panel links:** `__dashboardUid__` and `__panelId__` annotations put `dashboardURL` and `panelURL` into the payload.
- **Timers:** `repeat_interval` is rounded to a multiple of `group_interval` and capped at 5 days.
- **Mute timings:** include the start and exclude the end, in UTC unless `location` is set. Silences are one-off and can't be
  provisioned. Whether an alert that fired while muted is delivered afterwards is undocumented; test it once.
- **Webhook security:** `hmacConfig` (HMAC-SHA256 of `timestamp:body`) stops local processes from forging alert files.
  [Webhook](https://grafana.com/docs/grafana/v12.4/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/).

## 3. Dashboards

- **For a once-a-day reader:** a 24 h default range, panel descriptions, percentages, stacking off, colours from thresholds.
- **Per-GPU grid:** status history suits it better than a heatmap.
- **Per queue:** with two queues, one panel with `{{queue}}` legends beats repeated panels.
- **Joins:** in PromQL, not with the "Join by field" transformation.
- **Units:** `PROF_*` metrics are ratios (Percent 0.0–1.0); `GPU_UTIL` is 0–100.
- **Speed:** query type Range on graphs and Instant on stat panels (the default, Both, runs both); reuse one query through the
  Dashboard data source.

## 4. Prometheus

- **Data source:** `timeInterval: "1m"`, which we set, so `$__rate_interval` suits a 1-minute scrape. `httpMethod: POST`,
  `cacheLevel: High`.
- **Recording rules:** Grafana-managed ones need a Prometheus that accepts writes. Otherwise define them in Prometheus itself.
- **The join:** `* on(namespace,pod) group_left(queue)` needs each pod in exactly one queue. It would be simpler if our exporter used
  `pod`/`namespace` label names. It can't: service discovery sets those on the exporter's own target, which is why it uses
  `holder_*`.

## 5. Security and upgrades

- **Exposure:** hostNetwork on 127.0.0.1 is reachable by every local process, so keep anonymous access off. Consider
  `enforce_domain = true` with `domain = localhost`, and protecting `/metrics`.
- **`root_url`:** `http://localhost:3000/`.
- **Secrets from files:** `admin_password` applies only on first run, so load it and a fixed `secret_key` with `$__file{}` from a
  Secret.
- **Cookies:** keep `cookie_samesite = lax`.
- **Upgrades:** 12.4 gets patches until 24 May 2027. Grafana 13 migrates storage one way, so back up first, and use 13.0.1 or later.
  [Upgrade guide](https://grafana.com/docs/grafana/latest/upgrade-guide/upgrade-v13.0/).

## Recommended alerting settings (the report's numbers)

1. **Evaluation group:** one, at 1m, in folder Nebius.
2. **Rule 1:** `100 * max by (gpu)(max_over_time(DCGM_FI_PROF_GR_ENGINE_ACTIVE[15m]))`, condition `$A < 5 && $B > 0`, `for: 1m`,
   `keepFiringFor: 5m`.
3. **Rule 2:** `max_over_time(…{pod!=""}[10m]) < 0.01`, `for: 1m`, `noDataState: OK`.
4. **Policy:** `group_by: [alertname]`, `group_wait: 1m`, `group_interval: 10m`, `repeat_interval: 24h`.
5. **Mute timing:** `quiet-hour` 12:30–13:30 UTC, on the child policy.
6. **Data source:** `timeInterval: 1m`, `queryTimeout: 60s`.
7. **Provider and refresh:** `updateIntervalSeconds: 30`, dashboards refreshing every 5m, `min_refresh_interval = 1m`.
