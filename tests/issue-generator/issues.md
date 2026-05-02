# Apache Superset Test Issues

Issues sourced from [apache/superset](https://github.com/apache/superset) for testing the remediation system.
Each issue is created against the target repository by the issue generator container.
Issues are removed from this file after successful creation.

**Total: 50 issues** (Bug: 16, Feature: 17, Task: 17)

## Bug

### [Bug] UI Overlap and Inconsistent Chart Display in Dashboard Layout

**Source:** [https://github.com/apache/superset/issues/35080](https://github.com/apache/superset/issues/35080)
**Type:** Bug

### Bug description

<img width="696" height="314" alt="Image" src="https://github.com/user-attachments/assets/eb53e269-db74-402e-9689-cda30d539d47" />

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Bug] Unexpected focus outline (blue border) on Filter Badge popover

**Source:** [https://github.com/apache/superset/issues/38789](https://github.com/apache/superset/issues/38789)
**Type:** Bug

### Bug description
After page refresh, when hovering over the Filter Badge (indicator showing the count of applied filters) on a dashboard chart, a default blue focus outline appears around the popover container. This visual artifact is inconsistent with the rest of the Superset UI.

### How to reproduce the bug
1. Open a dashboard with filters and apply filters.
2. Refresh the page
3. Hover over the Filter Badge (the "1" or "2" icon next to the filter funnel).
4. Observe the blue border appearing around the "Applied filters" popover.

### Screenshots/recordings

https://github.com/user-attachments/assets/f49e35ef-ae4f-460e-a194-220fb4ba0b7a

### Superset version
master / latest-dev

### Python version
3.9

### Node version
16

### Browser
Chrome

### Additional context
No response

### Checklist
- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Bug] Treemap tooltip  css

**Source:** [https://github.com/apache/superset/issues/33896](https://github.com/apache/superset/issues/33896)
**Type:** Bug

I create treemap chart.  I found text appears cramped in the hover tooltip.  How  can I  make it more beautiful?

![Image](https://github.com/user-attachments/assets/ff9b46e7-7247-40e1-b85b-0a60ac64fb50)

---

### [Bug] UX: User should see an explanation for why they can't overwrite a chart when they don't own it

**Source:** [https://github.com/apache/superset/issues/39786](https://github.com/apache/superset/issues/39786)
**Type:** Bug

### Bug description

As an admin, I can see and edit any chart. But then I go to "Save Overwrite" and that's not an option. I get confused. Then I remember I need to be an owner of the chart.

Very related to https://github.com/apache/superset/issues/24399 but there they are proposing + linking to a fix that the admin can do the behavior. I am proposing a lighter fix: if the user doesn't have the permissions to overwrite the chart, it should say below the grayed-out option, "Must be a chart owner to overwrite the existing chart." That provides a better UX.

### Screenshots/recordings

Here's where I think this message should appear: 

<img width="921" height="278" alt="Image" src="https://github.com/user-attachments/assets/07b1f610-fcc1-471a-ab21-ee705876875a" />

### Superset version

6.0.0

### Python version

Not applicable

### Node version

Not applicable

### Browser

Not applicable

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Bug] labels are hard to read on pie chart

**Source:** [https://github.com/apache/superset/issues/39643](https://github.com/apache/superset/issues/39643)
**Type:** Bug

## Screenshot

<img width="334" height="383" alt="Image" src="https://github.com/user-attachments/assets/ee1b7949-9449-4576-a970-501169dd2e2f" />

## Description

On Pie chart, when using longer metrics names, they are cut off/not readable. unsure what the best approach would be. Tooltip would help.

## Design input
Would be great for designer to suggest how to improve this

---

### [Bug] Hiding "Metrics" section also collapses "Columns" section unexpectedly

**Source:** [https://github.com/apache/superset/issues/37444](https://github.com/apache/superset/issues/37444)
**Type:** Bug

### Bug description

**Problem**
When the Metrics section is collapsed (by clicking the ^ arrow), the Columns section also disappears from view — even though it should remain visible independently. This behavior breaks UI expectations and makes column selection impossible until Metrics are expanded again.

**Steps to Reproduce**
Open a chart or dataset in Superset.
In the "Metrics & Columns" panel, click the ^ arrow next to Metrics to collapse it.
Observe that the Columns section vanishes along with Metrics.

**Expected Behavior**
Collapsing the Metrics section should only hide the metrics list. The Columns section should remain fully visible and accessible unless explicitly collapsed by its own toggle.

**Impact**
This bug hinders user workflow, especially when users need to select columns while keeping metrics hidden for clarity. It’s particularly problematic in datasets with many columns.

### Screenshots/recordings

Before: Both Metrics and Columns are visible.

<img width="367" height="491" alt="Image" src="https://github.com/user-attachments/assets/0b0d10f9-4364-4a0d-8780-3fc18248b3e6" />

After: Only Metrics header remains; Columns section is gone.

<img width="403" height="288" alt="Image" src="https://github.com/user-attachments/assets/3ddf71f5-0cbe-44f4-a746-b84f7b60f25d" />

### Superset version

5.0.0

### Python version

3.9

### Node version

I don't know

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Bug] Bar chart rendering of a single data point is too wide

**Source:** [https://github.com/apache/superset/issues/33056](https://github.com/apache/superset/issues/33056)
**Type:** Bug

## Screenshot

<img width="750" alt="Image" src="https://github.com/user-attachments/assets/78e93207-079e-4d5a-9108-d957b0e3f4b1" />
<img width="708" alt="Image" src="https://github.com/user-attachments/assets/95e6cc5d-b3e4-48b1-8467-08864ad06f09" />

## Description

If there is only one single datapoint the bar gets too wide, it doesn't look nice and it can be confusing (as if there are multiple data points with the same value). When there are two data points or more this doesn't happen. My suggestion is to make the bar not wider than one 'tick' on the x-axis. 

I'm seeing this on 4.1.1 on the regular bar charts and the mixed charts.

---

### [Bug] Dark Theme: Starburst chart "total" displayed in black, labels in white with black outline

**Source:** [https://github.com/apache/superset/issues/37905](https://github.com/apache/superset/issues/37905)
**Type:** Bug

## Screenshot

<img width="1599" height="796" alt="Image" src="https://github.com/user-attachments/assets/64267819-342a-4476-8f06-18a1fb5ebf27" />

## Description

1. With the dark theme / dark mode on AND "show total" checked for a sunburst chart, the total value (displayed at the center of the chart) is displayed in black text with the dark theme background, making it virtually illegible.
2. The labels for the starburst chart when dark theme/mode is active appear as white text with a black outline. Even at a fairly large size this makes them difficult to read.

## Design input

1. `design:suggest` display total value using white/light foregrounded text color when dark theme/mode is active.
2. `design:suggest` display labels in either white/light or black/dark text with no outline. If the colors used by the theme are sufficiently bright but saturated (as they are in this screenshot), either should work, though white/light might be preferred.

---

### [Bug] Legend margin control does not work on radar charts, which can make labels overlap with the legend

**Source:** [https://github.com/apache/superset/issues/39424](https://github.com/apache/superset/issues/39424)
**Type:** Bug

## Screenshot

<img width="652" height="340" alt="Image" src="https://github.com/user-attachments/assets/18e5f07b-3033-47b3-9255-48c865019c15" />

## Description

Legend margin control does not work on radar charts, which can make labels overlap with the legend depending on the size of the chart.

## To reproduce

Create a Radar Chart with at least 3–5 categories/series so legend is visible. Then, in the control panel:
- Enable Show legend.
- Set legend position to Top, then try to change the legend margin (e.g. 0, 20, 60, 120).
- Repeat for Left, Right, and Bottom.

The radar chart doesn't move, and in cases where the chart height is small, axis labels at the top of the chart can overlap with the legend, as seen in the picture above.

---

### [Bug] Treemap chart color issue

**Source:** [https://github.com/apache/superset/issues/36807](https://github.com/apache/superset/issues/36807)
**Type:** Bug

### Bug description

Bug Description: 
1. Treemap chart's coloring seems to be only categorical, and not sequential/linear.
2. There seems to be a 1px wide gap around the key and or value text.

- Superset 4.1.1: Have sequential/linear coloring, did not have the gap.  
- Superset 4.1.4: Categorical coloring only, did not have the gap.
- Superset 6.0.0: Categorical coloring only, have the 1px gap.

Changing Color Scheme had no effect beyond changing the colors used. No custom CSS were used.
I could test other versions, if that would be of help.



### Screenshots/recordings

1. 6.0.0/4.1.4:

<img width="1200" height="471" alt="Image" src="https://github.com/user-attachments/assets/e8673a8a-0966-448a-b57f-4636e846300a" />

2. 4.1.1 (ideal)

<img width="1200" height="471" alt="Image" src="https://github.com/user-attachments/assets/3659e923-ed50-4ad6-974c-e6fd42a5650c" />

### Superset version

6.0.0

### Python version

3.11

### Node version

I don't know

### Browser

Chrome

### Additional context

- Error persists in Chrome and Firefox.
- No error message in browser console or in the log.
- Built custom image based on 6.0.0. Dockerfile:
```Dockerfile
 FROM apache/superset:6.0.0

 USER root

 ENV BUILD_TRANSLATIONS="true"

 RUN apt update
 RUN apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

 RUN . /app/.venv/bin/activate
 RUN uv pip install \
     psycopg2-binary \
     mysqlclient \
     Authlib

 USER superset
 CMD ["/app/docker/entrypoints/run-server.sh"]
```

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Bug] Permissions dropdown shows duplicated items after scrolling (Superset 6.0.0)

**Source:** [https://github.com/apache/superset/issues/39095](https://github.com/apache/superset/issues/39095)
**Type:** Bug

### Bug description

#### Description

When editing a role in Superset, the **Permissions dropdown** initially renders correctly. However, after scrolling through the list, duplicate entries begin to appear (e.g., repeated `can download RoleModelView`).

This appears to be a **frontend rendering issue**, as the duplication only manifests after user interaction (scrolling), not on initial load.

---

#### Expected Behavior

* Each permission should appear **only once** in the dropdown
* Scrolling should not introduce duplicate entries

---

#### Actual Behavior

* After scrolling the dropdown list, multiple identical entries are rendered
* Example: `can download RoleModelView` appears repeatedly
* The issue worsens with continued scrolling

---

#### Steps to Reproduce

1. Go to **Security → List Roles**
2. Edit any role (or create a new one)
3. Open the **Permissions dropdown**
4. Scroll down through the list
5. Observe duplicated entries appearing

### Screenshots/recordings

<img width="608" height="620" alt="Image" src="https://github.com/user-attachments/assets/a2fd6cd0-839b-4dae-a92d-29d3c810b25e" />

### Superset version

6.0.0

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

* The issue does **not appear on initial render**
* It only occurs **after scrolling**

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Bug] Cosmetic Issue: permission box is too narrow

**Source:** [https://github.com/apache/superset/issues/39339](https://github.com/apache/superset/issues/39339)
**Type:** Bug

## Screenshot

<img width="1903" height="868" alt="Image" src="https://github.com/user-attachments/assets/7b56a123-4f1b-45aa-90d2-cdab843174af" />

## Description

Width of this dialog box is less than length of the options. Can not view the options properly.

---

### [Bug] Embedded Dashboard ignores spacing between charts

**Source:** [https://github.com/apache/superset/issues/36204](https://github.com/apache/superset/issues/36204)
**Type:** Bug

### Bug description

I have embedded the Sales Dashboard Demo in a test angular application using the superset embedded sdk. The embedded Dashboard is not showing me the same spacing as the original Dashboard.

Original: Has spacing between all charts

<img width="2558" height="1140" alt="Image" src="https://github.com/user-attachments/assets/d5bf5d69-b909-49f4-82f2-a7e64590af49" />

Embedded: No Spacing between charts and unnecessary horizontal scrollbar:

<img width="1944" height="1084" alt="Image" src="https://github.com/user-attachments/assets/b26a27f0-47bc-4ccb-b7cd-8167681b53b8" />

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

I don't know

### Node version

16

### Browser

Firefox

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Bug] Green/Red contrast colors doesn’t look great in dark mode, compared to light mode

**Source:** [https://github.com/apache/superset/issues/39213](https://github.com/apache/superset/issues/39213)
**Type:** Bug

## Screenshot
<img width="419" height="187" alt="Image" src="https://github.com/user-attachments/assets/b3597378-463f-4b4f-a61a-450d98550744" />

## Description

Green/Red contrast colors doesn’t look great in dark mode, compared to light mode

## Design input
Needs design input

---

### [Bug] Gantt chart y axis labels are cut off

**Source:** [https://github.com/apache/superset/issues/38844](https://github.com/apache/superset/issues/38844)
**Type:** Bug

## Screenshot

<img width="1690" height="1041" alt="Image" src="https://github.com/user-attachments/assets/66f80f5c-ed8a-490a-8d84-1ed23c077f8e" />

## Description

Gantt charts y axis labels are cut off

---

### [Bug] Dropdown menu shows 2 scroll bars.

**Source:** [https://github.com/apache/superset/issues/35833](https://github.com/apache/superset/issues/35833)
**Type:** Bug

## Screenshot

<img width="1508" height="880" alt="Image" src="https://github.com/user-attachments/assets/576e9149-a8a0-453d-a410-13488acc2385" />

## Description

The dropdown menu shows 2 scroll bars. 
Using Superset 6.0.0rc2

## Design input
`design:suggest`
Should show only 1 scroll bar.

---

## Feature

### [Feature] [SIP-195] Support SQL-based querying on MongoDB.

**Source:** [https://github.com/apache/superset/issues/36844](https://github.com/apache/superset/issues/36844)
**Type:** Feature

*Please make sure you are familiar with the SIP process documented*
[here](https://github.com/apache/superset/issues/5602). The SIP will be numbered by a committer upon acceptance.

## [SIP] Proposal for Supporting SQL-based querying on MongoDB.<title>

### Motivation

Apache Superset provides a rich SQL-based analytical experience, but it currently lacks a connector for NoSQL databases such as MongoDB. Providing SQL-based querying support for MongoDB would significantly improve Superset’s usability, lower the learning curve for analysts, and enable more real-time analytics directly on MongoDB data.

### Proposed Change

I have created a DB API 2.0–compliant project that allows users to query MongoDB using SQL. A SQLAlchemy dialect has already been implemented in the project. The remaining work is to add MongoDB as a new engine in db_engine_specs, and to complete the unit tests and documentation.

Project space: [https://github.com/passren/PyMongoSQL](https://github.com/passren/PyMongoSQL)

The proposed connection string would be:
`mongodb://<user>:<password>@<host>:<port>/<database>?mode=superset`
`mongodb+srv://<user>:<password>@<host>:<port>/<database>?mode=superset`

### New or Changed Public Interfaces

No changes to Public Interfaces

### New dependencies

PyMongoSQL is required as a dependency and is maintained by me. I am also the author of [PyDynamoDB](https://github.com/passren/PyDynamoDB) which is the connector to dynamodb for superset, which follows a similar design and maintenance model. The license is MIT.

`pip install pymongosql`

### Migration Plan and Compatibility

No migration is required. PyMongoSQL supports both SQLAlchemy 1.x and 2.x.

### Rejected Alternatives

No

---

### [Feature] Show value on stacked bar chart is incorrect

**Source:** [https://github.com/apache/superset/issues/33882](https://github.com/apache/superset/issues/33882)
**Type:** Feature

### Bug description

The stacking functionality for bar charts was introduced recently, but it broke the option to show bar values.

When selecting Only Total, then Instead of displaying the number for each bar, it now shows a single value for the entire cluster. In the example below, it should show two separate numbers, not just one.
![Image](https://github.com/user-attachments/assets/8c322e4c-62fb-47bf-b8ca-fb60817d2304)



When Only Total is unselected, it is completely broken
![Image](https://github.com/user-attachments/assets/54eeb504-faf1-43ee-8e34-92db824f6daa)




### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Feature] Bug : Celery broken with Redis Cluster in 5.0.0, async queries and reports not working

**Source:** [https://github.com/apache/superset/issues/36294](https://github.com/apache/superset/issues/36294)
**Type:** Feature

### Bug description

I'm not sure if this is a bug or a configuration issue, but here's what we're experiencing...

We're running into an issue with the new 5.0.0 release where Celery completely breaks when we try to use a Redis Cluster as the broker and result backend. This is taking down two critical features for us:
1.SQL Lab async queries just fail with "Failed to start remote query on a worker"
2.All scheduled reports stop working and won't generate

### Screenshots/recordings

Here's the relevant part from our superset_config.py 
# Trying to use Redis Cluster for Celery
class CeleryConfig(object):
    broker_url = "redis://our-redis-cluster-host:port"  # Our cluster connection string
    result_backend = "redis://our-redis-cluster-host:port"  # Same here
    imports = ("superset.sql_lab", "superset.tasks.scheduler",)
    worker_prefetch_multiplier = 10
    task_acks_late = True

CELERY_CONFIG = CeleryConfig

# Enable async SQL Lab
SQLLAB_EXECUTOR = "superset.sql_lab.CeleryAsyncExecutor"

# Enable reports
FEATURE_FLAGS = {
    "ENABLE_ASYNC_QUERIES": True,
    "ASYNC_QUERIES": True,
    "GLOBAL_ASYNC_QUERIES": False,
}


Troubleshooting we've tried:

We even tried using the solo pool instead of prefork to avoid any potential cluster issues, by running:

celery --app=superset.tasks.celery_app:app worker --pool=solo -O fair -c 4

But the issue persists - Celery still fails to work properly with the Redis Cluster setup.

What we expect:

Pretty straightforward - we expect Superset 5.0.0 to properly support Redis Cluster as Celery backend so async queries and reports work normally.

### Superset version

5.0.0

### Python version

3.11

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a

... (truncated)

---

### [Feature] Feature request: stacked grouped mixed chart

**Source:** [https://github.com/apache/superset/issues/32496](https://github.com/apache/superset/issues/32496)
**Type:** Feature

Business requirement specification based on https://github.com/apache/superset/discussions/28181

### Request

We need a bar chart that supports both **grouping and stacking** simultaneously. The X-axis should handle **arbitrary data or time series**. Additionally, the chart must support a **mixed format** (e.g., bar + line overlay) and include **trend lines**.  

### Example Use Case:  
We currently track the ratio of **User Stories delivered in Sprint N** to **Bugs opened in Sprint N** (split by P1 and P2/P3). An efficiency line (#User Stories / #Bugs Open) helps visualize team performance, while a **trend line for P1 bugs** highlights patterns over time.  

This is critical for maintaining product quality as we scale. As technical debt grows, bug influx can impact efficiency. Tracking these metrics ensures we maintain high standards while keeping the product competitive.

### Google Sheet implementation 
Example of implementation using Google Sheet: https://docs.google.com/spreadsheets/d/1G3rntcOYkf9Uwz4yBHDFOsfgV87RT0UMh15HbxTXlh4/edit?usp=sharing

The chart groups **User Stories (blue bars)** and **Bugs (red + yellow bars)** by Agile sprints. At the same time, **Bugs are stacked** to show priority levels (**red for Priority 1, yellow for Priority 2/3**).  

The **green line** represents efficiency across sprints, while the **light red line** is an automatically calculated **trend line for Priority 1 Bugs**.


![Image](https://github.com/user-attachments/assets/31c1fab7-ad51-4cf0-8f04-39531d230933)

---

### [Feature] Enable Superset embed dashboard, some request interfaces report error 404

**Source:** [https://github.com/apache/superset/issues/34813](https://github.com/apache/superset/issues/34813)
**Type:** Feature

### Bug description

The error scenario is as follows in Version: 4.1.1:
1. Right click on Chart to open _ChartContextMenu_. _DrillByMenuItems_ will request the **/api/v1/dataset/id** interface, which will report an error: **404 NOT FOUND**.
2. Granting the visitor user **can_samples** permission, _DrillModal_ opened in _DrillDetailMenuItems_ within _SliceHeaderControl_ will also request **/api/v1/dataset/id** with an error message of **404 NOT FOUND**
3. I have added some custom requirements in _DrillByMenuItems_, which use **/api/v1/deploy/?slice_id=*** Successfully obtained slice data, but failed to retrieve chart data using **/api/v1/chart/id** with error: 404 NOT FOUND. When the error occurs, use the ChartContextMenu to refresh and request interface **/api/v1/chart/data?form_data=*...** Error: 403 FORBIDDEN

### Screenshots/recordings

_No response_

### Superset version

4.1.3

### Python version

3.10

### Node version

18 or greater

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [ ] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [ ] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Feature] Embbeded dashboards with GAQ feature enabled does not work

**Source:** [https://github.com/apache/superset/issues/34611](https://github.com/apache/superset/issues/34611)
**Type:** Feature

### Bug description

Enable GLOBAL_ASYNC_QUERIES feature and use any embedded dashboard.

Load the page and you will get 401 UNAUTHORIZED response.

WARNING:root:Failed to add user to db session: Class 'werkzeug.local.LocalProxy' is not mapped
WARNING:root:Failed to add user to db session: Class 'werkzeug.local.LocalProxy' is not mapped
WARNING:superset.common.utils.query_cache_manager:force_cached (QueryContext): value not found for key 68d2a3488fa8bc378f473740ea4157ef
WARNING:superset.async_events.async_query_manager:Parse jwt failed
Traceback (most recent call last):
  File "/app/superset/async_events/async_query_manager.py", line 203, in parse_channel_id_from_request
    return jwt.decode(token, self._jwt_secret, algorithms=["HS256"])["channel"]
  File "/app/.venv/lib/python3.10/site-packages/jwt/api_jwt.py", line 222, in decode
    decoded = self.decode_complete(
  File "/app/.venv/lib/python3.10/site-packages/jwt/api_jwt.py", line 167, in decode_complete
    self._validate_claims(
  File "/app/.venv/lib/python3.10/site-packages/jwt/api_jwt.py", line 273, in _validate_claims
    self._validate_sub(payload, subject)
  File "/app/.venv/lib/python3.10/site-packages/jwt/api_jwt.py", line 300, in _validate_sub
    raise InvalidSubjectError("Subject must be a string")
jwt.exceptions.InvalidSubjectError: Subject must be a string


The root cause is that sub claim is not set on async_access cookie token [register_request_handlers](https://github.com/apache/superset/blob/2696d3e8004db8e5a3e83a96a3b2cb0b60de327c/superset/async_events/async_query_manager.py#L165):

`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaGFubmVsIjoiZjc4OTk5ZTUtMjZjYi00ODg5LTgzZDQtMWEyZTE2NGIzNzM2Iiwic3ViIjpudWxsfQ.jWwEk5mHJjUHvCBKKcKayjIF9LNgkVYYxZ_HPenUhBo`

There fore [parse_channel_id_from_request](https://github.com/apache/superset/blob/2696d3e8004db8e5a3e83a96a3b2cb0b60de327c/superset/async_events/async_query_manager.py#L197C9-L197C38) throws jwt.exceptions.InvalidSubjectError: Subject must be a s

... (truncated)

---

### [Feature] Table chart "Show totals" row truncates decimals (uses parseInt) when Time Comparison is enabled

**Source:** [https://github.com/apache/superset/issues/39717](https://github.com/apache/superset/issues/39717)
**Type:** Feature

### Bug description

When a Table chart is configured with:
- Show totals = ON
- Time Comparison enabled (`time_compare` set, `comparison_type = "values"`)

…the summary/totals row shows numbers truncated to integers. The bug lives in `processComparisonTotals` in superset-frontend/plugins/plugin-chart-table/src/transformProps.ts (present in 5.0.0, 6.0.0, and master). Three accumulator lines coerce the totals via `parseInt(x, 10)` instead of `Number(x)` / `parseFloat(x)`:

    transformedTotals[`Main ${key}`] =
      parseInt(transformedTotals[`Main ${key}`]?.toString() || '0', 10) +
      parseInt(totalRecord[key]?.toString() || '0', 10);
    transformedTotals[`# ${key}`] =
      parseInt(transformedTotals[`# ${key}`]?.toString() || '0', 10) +
      parseInt(totalRecord[`${key}__${comparisonSuffix}`]?.toString() || '0', 10);

Consequences:
- Decimal metrics lose their fractional part (e.g. 12,345.67 → 12,345).
- Ratio/percent metrics in the 0–1 range collapse to 0 (e.g. SAFE_DIVIDE(SUM(GrossMargin), SUM(GrossSales)) ≈ 0.6881 becomes 0, displayed as "0.0%").
- Because the derived `△` (delta) and `%` columns are computed from those truncated `Main`/`#` values via `calculateDifferences`, they also collapse to 0 / 0%.

Without time comparison, totals come straight from `totalQuery?.data[0]` with no parseInt and are correct, which is why this only manifests when Time Comparison is on.

Repro:

1. Build a Table chart on any dataset with a ratio metric, e.g. SAFE_DIVIDE(SUM(numerator), SUM(denominator)) formatted as `.1%`.
2. Add at least one groupby dimension.
3. Toggle "Show summary" ON.
4. Set Time Comparison range (e.g. "365 day ago"),
5. Comparison type = "Values".
6. Observe the summary row: Main / # / △ / % all render as 0 / 0.0%.
7. Verify via /api/v1/chart/data that the totals query itself returns the correct ratio; the bug is purely in the frontend transformProps.

Expected:
Summary row shows the same value the totals query returns (i.e. SAFE_DIVIDE on the global

... (truncated)

---

### [Feature] LDAP/OAuth authentication should NOT enable public/open registration via UI by default

**Source:** [https://github.com/apache/superset/issues/37100](https://github.com/apache/superset/issues/37100)
**Type:** Feature

### Bug description

For LDAP/OAuth authentication to work, AUTH_USER_REGISTRATION must be set to True (in superset_config.py) in order to allow syncing of Superset DB with LDAP/OAuth provider.

However, 'AUTH_USER_REGISTRATION = True' also enables registration path on Superset UI (registration button,etc.). This is a potential security hole, and there are numerous use cases where this is HIGHLY undesirable.

Open/public registration should be optional and disabled by default for any type of authentication, including LDAP/OAuth.

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [ ] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [ ] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Feature] init-db job does not complete when istio service mesh is enabled on the superset namespace in Kubernetes

**Source:** [https://github.com/apache/superset/issues/25798](https://github.com/apache/superset/issues/25798)
**Type:** Feature

The init-db job never reaches Completed when Istio automatic sidecar injection is enabled on the superset namespace.

#### How to reproduce the bug

1. Deploy kubernetes
2. Enable istio injection on the superset namespace
3. Deploy superset
4. Watch the init-db Job

### Expected results
initi-db should reach the Completed state.

### Actual results
The init-db container exits, but the injected envoy-proxy continues to run.

---

### [Feature] Getting error when using RLS filtering in Guest token when GLOBAL_ASYNC_QUERIES is enabled

**Source:** [https://github.com/apache/superset/issues/31492](https://github.com/apache/superset/issues/31492)
**Type:** Feature

### Bug description

I am getting an error:

"This session has encountered an interruption, and some controls may not work as intended. If you are the developer of this app, please check that the guest token is being generated correctly."

when using RLS filter in GuestToken for embedded dashboard when "GLOBAL_ASYNC_QUERIES" = True. The same GuestToken set up works when  GLOBAL_ASYNC_QUERIES is not used
the errors I am getting in the dashboard network are "not authorised" for charts and filter apis and the above quoted message on the top
Note: 
I have celery worker and cache set up with a Redis server in both cases
token payload :

{
"user": {
"username": "guest",
"first_name": "guest",
"last_name": "guest"
},
"resources": [
{
"type": "dashboard",
"id": "d035c4d2-3e2c-4e3f-b45e-20ebb8b366e8"
}
],
"rls_rules": [
{
"clause": ""STATEID" = 3"
}
],
"iat": 1734112254.027939,
"exp": 1734112554.027939,
"aud": "http://0.0.0.0:8080/",
"type": "guest"
}

I have seen discussion and PR in
https://github.com/apache/superset/pull/18924
https://github.com/apache/superset/issues/24171
and some in slack also addressing this bug but it says it was solved from superset 3.1 and I am using latest superset in my docker pull

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.10

### Node version

I don't know

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [X] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [ ] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Feature] ECharts Bar Chart renders only currency symbol ($) when Show Value is enabled with stacked bars

**Source:** [https://github.com/apache/superset/issues/38037](https://github.com/apache/superset/issues/38037)
**Type:** Feature

### Bug description

Superset version:
5.0.0

Chart type:
ECharts Bar Chart

Configuration:
- Stacked bar
- Show Value enabled
- Currency prefix ($)
- Near-zero negative values
- Row limit: 50

Steps to reproduce:
1. Create dataset with mostly small negative values (e.g. -1 to -5)
2. Add one large negative outlier (e.g. -4,000,000)
3. Create ECharts Bar Chart
4. Enable stacked bars
5. Enable "Show Value"
6. Apply currency prefix ($)

Expected behavior:
Numeric values should render correctly with currency formatting (e.g., $1,234), and should not display only the currency symbol.

Actual behavior:
Only the currency symbol "$" is rendered repeatedly without numeric values, particularly for near-zero values.
Occurs in both horizontal and vertical orientation.

<img width="1468" height="774" alt="Image" src="https://github.com/user-attachments/assets/caaccd2f-73e6-48ab-84be-e98d0fdf73d8" />

<img width="1466" height="779" alt="Image" src="https://github.com/user-attachments/assets/0add6564-7736-43b5-9af0-aff2ceb88ca1" />

[warehouse_handling_dummy_data.csv](https://github.com/user-attachments/files/25383785/warehouse_handling_dummy_data.csv)

Browser:
Google Chrome 143.0.7499.193 (Official Build) (arm64)


### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Feature] ENABLE_SUPERSET_META_DB feature works incorrectly

**Source:** [https://github.com/apache/superset/issues/36304](https://github.com/apache/superset/issues/36304)
**Type:** Feature

### Bug description

I use MS SQL and MongoDb (through Trino).

When I try to execute query like this one below:

SELECT t1.DeviceId, t2.timestamp, t1.Name, t2.hash, t1.DeviceTypeId
FROM "MagistralDb.dbo.Devices" AS t1
INNER JOIN "Mongo.bluetoothdb.scans" as t2 ON t2.deviceid = t1.DeviceId
**WHERE t1.DeviceId = 2560 OR t1.DeviceId = 2562 OR t1.DeviceId = 2564 OR t1.DeviceId = 2565**

I got the message: **"The query returned no data"**

If I cut "WHERE" condition to "WHERE t1.DeviceId = 2560", so my query is:

SELECT t1.DeviceId, t2.timestamp, t1.Name, t2.hash, t1.DeviceTypeId
FROM "MagistralDb.dbo.Devices" AS t1
INNER JOIN "Mongo.bluetoothdb.scans" as t2 ON t2.deviceid = t1.DeviceId
**WHERE t1.DeviceId = 2560**

I got **1K records**

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Feature] Superset is adding the escape character for '\' character in filter value, resulting to zero records filtered

**Source:** [https://github.com/apache/superset/issues/38453](https://github.com/apache/superset/issues/38453)
**Type:** Feature

### Bug description

Using 

- Superset 6.0
- Duckdb 1.3.0
- Duckdb Engine 0.17.0

We have data, in that one column that is columnA, which is having back slash in value (name\email) 

1. When user add a filter for columnA
2. when user select the value from the columnA filter (Value will be name\email)
3. click on apply
4. Chart load with zero records, but records exist with value name\email in columnA
5. When we inspect the query, query add escape character in the filtered value, query looks as below
Query: SELECT ColumnA, ColumnB from TABLE where columnA IN ("name\\\\email")

ISSUE:
Because of adding the one more backslash to the value, query is returning zero records, even though values exist.
Please let us know, how we can resolve this issue

Thanks in advance
Nagaraj M M

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Feature] Superset V6 . new filter is adding two input control

**Source:** [https://github.com/apache/superset/issues/37265](https://github.com/apache/superset/issues/37265)
**Type:** Feature

### Bug description

In Dashboard , while adding filter ,getting two input as part of new feature this is not recommended for most of the customers.. can we remove it and keep like previous version.

<img width="376" height="142" alt="Image" src="https://github.com/user-attachments/assets/ddaa2858-9abf-4f7b-acf1-a5b2629c4853" />

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [ ] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [ ] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Feature] test(e2e): Add Playwright test for time range pre-filter visibility based on dataset columns

**Source:** [https://github.com/apache/superset/issues/36964](https://github.com/apache/superset/issues/36964)
**Type:** Feature

## Summary

Add a Playwright E2E test to verify that the time range pre-filter option is hidden when a dataset has no temporal columns.

## Background

This test scenario was originally implemented as a Jest/RTL unit test in `FiltersConfigModal.test.tsx` but was skipped in September 2021 (PR #16906) due to flakiness. After 11 fix attempts, it was determined that this scenario cannot be reliably tested at the unit test level due to:

1. The modal architecture requires complex Redux + API mock coordination
2. `showTimeRangePicker` depends on `loadedDatasets` populated by async API fetch during mount
3. Timing issues between state updates and component rendering create race conditions

The underlying logic is now covered by unit tests for `shouldShowTimeRangePicker` and `hasTemporalColumns` in `utils.test.ts`.

## Test Scenario

1. Create/edit a filter with a dataset that has **no temporal columns** (only String, Numeric, Boolean types)
2. Open the filter configuration modal
3. Navigate to the Settings tab
4. Enable the pre-filter checkbox
5. **Verify**: The time range pre-filter option should NOT be shown

## Acceptance Criteria

- [ ] Playwright test covers the scenario described above
- [ ] Test uses a dataset fixture with `column_types` containing no `GenericDataType.Temporal` (value 2)
- [ ] Test is stable and not flaky

## Related

- PR #36012 - Removed the skipped Jest test
- Original feature: PR #15225 (June 2021)
- Original skip: PR #16906 (September 2021)

---

### [Feature] [SIP-179] Proposal for Enhanced Aggregation Customization in Totals/Subtotals

**Source:** [https://github.com/apache/superset/issues/34245](https://github.com/apache/superset/issues/34245)
**Type:** Feature

<html>
<body>
<!--StartFragment--><h2 data-start="132" data-end="208">[SIP] Proposal for Enhanced Aggregation Customization in Totals/Subtotals</h2>
<h3 data-start="210" data-end="224">Motivation</h3>
<p data-start="226" data-end="503">Currently, Apache Superset applies the same aggregation function across all fields when rendering row and column <strong data-start="339" data-end="349">totals</strong> and <strong data-start="354" data-end="367">subtotals</strong> in pivot tables and similar visualizations. This creates a limitation when users need different aggregation logic for different fields.</p>
<p data-start="505" data-end="518">For instance:</p>
<ul data-start="519" data-end="849">
<li data-start="519" data-end="684">
<p data-start="521" data-end="684">A user may want <strong data-start="537" data-end="544">SUM</strong> to be applied on a metric like <code data-start="576" data-end="602">"Total Disbursed Amount"</code> and <strong data-start="607" data-end="618">AVERAGE</strong> or <strong data-start="622" data-end="647">custom % contribution</strong> on another metric like <code data-start="671" data-end="683">"% Booked"</code>.</p>
</li>
<li data-start="685" data-end="849">
<p data-start="687" data-end="849">Currently, this is not supported — once a total/subtotal aggregation function is selected, it applies uniformly to all fields in both row and column aggregations.</p>
</li>
</ul>
<p data-start="851" data-end="1027">This constraint reduces the flexibility and usability of dashboards with multi-metric visualizations where different fields inherently require different aggregation strategies.</p>
<h3 data-start="1029" data-end="1048">Proposed Change</h3>
<p data-start="1050" data-end="1175">Introduce support for <strong data-start="1072" data-end="1113">field-level aggregation customization</strong> in the totals and subtotals logic. This could be achieved by:</p>
<ol data-start="1177" data-end="1558">
<li data-start="1177" data-end="1289">
<p data-start="1

... (truncated)

---

### [Feature] [SIP-176] Proposal for Enhanced OAuth2 Access Token Management UI and Performance Optimization in Apache Superset

**Source:** [https://github.com/apache/superset/issues/33969](https://github.com/apache/superset/issues/33969)
**Type:** Feature

## [SIP-176] Proposal for Enhanced OAuth2 Access Token Management UI and Performance Optimization in Apache Superset

### Motivation

While attempting to ingest Apache Superset metadata using a third-party tool, I observed that access tokens can only be generated via the Swagger API and not through the Superset UI. Adding a UI component for token generation would significantly improve usability and accessibility.

Additionally, when running Superset using the Docker Compose deployment, I noticed excessive memory usage. This could be investigated and optimized to improve overall performance and reduce resource consumption.

as you can see here, only Superset services are using nearly 3 GB of RAM

![Image](https://github.com/user-attachments/assets/ca2bb074-cc6b-4610-953a-8f2d176d5c3c)

### Proposed Change

Propose a UI for managing access tokens, enabling users to easily generate and manage tokens, as well as benefit from the available endpoints that use them. If possible, allow for the creation of multiple tokens with different permissions to support flexible access control.

Regarding the official Superset images, it could be part of a broader plan to improve performance and reduce high system usage. While it may be a significant undertaking, it is a valuable consideration worth pursuing.

Implement a monitoring service to check Superset's performance and enhance the performance of certain images by switching to a lighter Linux base image for example.

### New or Changed Public Interfaces

As far as I know, no change is needed.

### New dependencies

cryptography Python library: this is essential for securely encrypting and decrypting OAuth2 access and refresh tokens stored in the new database table, ensuring tokens are protected at rest.

### Migration Plan and Compatibility

Add new table

table: `database_user_oauth2_tokens`

| Column Name     | Data Type   | Description                                                  |
|-----------------|-------------|--------

... (truncated)

---

## Task

### [Task] language_pack/ru/:1   Failed to load resource: the server responded with a status of 404 (NOT FOUND)

**Source:** [https://github.com/apache/superset/issues/35581](https://github.com/apache/superset/issues/35581)
**Type:** Task

### Bug description

After adding
` 
LANGUAGES = {
"ru": {"flag": "ru", "name": "Russian"},
"en": {"flag": "us", "name": "English"}
}

BABEL_DEFAULT_LOCALE = "ru"
`
 to the file, the language selection appeared, but selecting it produces an error in the logs.



<img width="957" height="247" alt="Image" src="https://github.com/user-attachments/assets/94d54c4f-733a-4db9-b5ac-6758041ca192" />

<img width="957" height="145" alt="Image" src="https://github.com/user-attachments/assets/a15f5ae5-d7d3-4837-8397-b08e3b311fe6" />

**### To reproduce:**
git clone https://github.com/apache/superset.git
in file superset_config.py
```
LANGUAGES = {
"ru": {"flag": "ru", "name": "Russian"},
"en": {"flag": "us", "name": "English"}
}

BABEL_DEFAULT_LOCALE = "ru"
```
docker compose -f docker-compose-non-dev.yml up

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Task] docker compose up --build fails on 5.0.0 with No matching distribution found for uv

**Source:** [https://github.com/apache/superset/issues/35607](https://github.com/apache/superset/issues/35607)
**Type:** Task

### Bug description


**Description:**
When trying to build Superset from the 5.0.0 tag using Docker Compose, the build fails due to a missing dependency `uv`.

**Steps to Reproduce:**
1. Clone the repo and checkout the 5.0.0 tag:
   ```bash
   git clone https://github.com/apache/superset.git
   cd superset/
   git fetch origin --tags
   git checkout -b dev 5.0.0
   ```
2. Run:
   ```bash
   docker compose up --build
   ```

**Observed Behavior:**
The build fails with the following error:
```
ERROR: Could not find a version that satisfies the requirement uv (from versions: none)
ERROR: No matching distribution found for uv
```

**Expected Behavior:**
The Docker image should build successfully without dependency resolution errors.

**Environment:**
- Superset version: 5.0.0 (tag)
- Docker version 28.3.2, build 578ccf6
- OS: Ubuntu 24.04

**Additional Context:**
It seems the `uv` package is not available on PyPI, which causes the build to fail. Possibly a missing or misconfigured dependency in `requirements` or `constraints`.



### Screenshots/recordings

_No response_

### Superset version

5.0.0

### Python version

3.11

### Node version

18 or greater

### Browser

Not applicable

### Additional context

```
docker compose up --build
[+] Building 292.8s (24/70)                                                                                                                                             
 => [internal] load local bake definitions                                                                                                                         0.0s
 => => reading from stdin 3.24kB                                                                                                                                   0.0s
 => [superset-websocket internal] load build definition from Dockerfile                                                                                            0.0s
 => => transferring dockerfile: 1.20kB                                

... (truncated)

---

### [Task] Cannot override admin credentials

**Source:** [https://github.com/apache/superset/issues/35550](https://github.com/apache/superset/issues/35550)
**Type:** Task

### Bug description

Hi Team,

I am trying to override the default admin password for Superset by setting ADMIN_PASSWORD in extraEnv, but it still uses the default password.

Even after a clean database installation, the issue persists. Please let me know if any additional configuration is required for the application to use the password I have defined.

### Screenshots/recordings

_No response_

### Superset version

5.0.0

### Python version

3.11

### Node version

18 or greater

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Task] TypeError: (intermediate value).difference is not a function  in version 5.0.0

**Source:** [https://github.com/apache/superset/issues/35583](https://github.com/apache/superset/issues/35583)
**Type:** Task

### Bug description

Hi,
I have an Apache Superset installation version 4.0.0 that works correctly.

I’m using the Docker image apache/superset:4.0.0 with a Postgres database, configured through a setup file and an initialization script that launches the command:

gunicorn --bind "0.0.0.0:$SUPERSET_PORT" "superset.app:create_app()" \
    --workers "$GUNICORN_WORKERS" \
    --threads "$GUNICORN_THREADS" \
    --timeout "$GUNICORN_TIMEOUT" \
    --max-requests "$GUNICORN_MAX_REQUESTS" \
    --preload


When I upgrade to version 5.0.0, using the image apache/superset:5.0.0, the application starts, applies the database migrations, and I can log in.

However, when I open some of the preloaded example dashboards, I get the following error:

TypeError: (intermediate value).difference is not a function at ka (http://localhost:8088/static/assets/3301108a09f8ea91dbb3.chunk.js:1195:162) at Pa (http://localhost:8088/static/assets/3301108a09f8ea91dbb3.chunk.js:1195:6713) at div at http://localhost:8088/static/assets/vendors.550cd2480f8c70dc73c1.entry.js:2:144917 at ko (http://localhost:8088/static/assets/3301108a09f8ea91dbb3.chunk.js:888:51) at div at div at http://localhost:8088/static/assets/vendors.550cd2480f8c70dc73c1.entry.js:2:144917 at ce (http://localhost:8088/static/assets/3301108a09f8ea91dbb3.chunk.js:199:51) at _ (http://localhost:8088/static/assets/3301108a09f8ea91dbb3.chunk.js:2:364292) at div at http://localhost:8088/static/assets/vendors.550cd2480f8c70dc73c1.entry.js:2:144917 at div at http://localhost:8088/static/assets/vendors.550cd2480f8c70dc73c1.entry.js:2:144917 at Pu (http://localhost:8088/static/assets/3301108a09f8ea91dbb3.chunk.js:2042:17) at Yu (http://localhost:8088/static/assets/3301108a09f8ea91dbb3.chunk.js:2297:54) at P (http://localhost:8088/static/assets/e2c4328768742c923137.chunk.js:1:2359) at g (http://localhost:8088/static/assets/vendors.550cd2480f8c70dc73c1.entry.js:2:1029958) at pe (http://localhost:8088/static/assets/e2c4328768742c923137.chunk

... (truncated)

---

### [Task] superset_init container exits as unhealthy despite successful Superset login

**Source:** [https://github.com/apache/superset/issues/35502](https://github.com/apache/superset/issues/35502)
**Type:** Task

### Bug description

The superset_init container exits after some time (~360s) and shows unhealthy, even though Superset itself works and login is successful.

I cloned the Superset repository (branch 5.0.0) and ran docker compose -f docker-compose-image-tag.yml up. After starting the containers, I checked their status using docker ps and docker-compose ps. I observed that the superset_init container shows as Exited and unhealthy, even though the Superset UI is accessible and I am able to log in without any issues.

### Screenshots/recordings

Please find attached the superset_init container logs along with environment details for reference.

Environment details:

[docker logs superset_init.txt](https://github.com/user-attachments/files/22692090/docker.logs.superset_init.txt)

OS: Ubuntu 24.04.3 LTS running via Windows 10 Pro (22H2, Build 19045.6396)
Superset version: 5.0.0
Python version (inside container): 3.10.18
Flask version: 2.3.3
Werkzeug version: 3.1.3
Docker version: 28.4.0, build d8eb465
Docker Compose version: v2.39.4-desktop.1

### Superset version

5.0.0

### Python version

3.10

### Node version

18 or greater

### Browser

Chrome

### Additional context

No feature flags or customizations enabled.
This occurs on a fresh setup with default docker-compose.

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Task] [6.0.0rc2] Fetch error NOT FOUND /api/v1/_openapi in Swagger after setting SUPERSET_APP_ROOT

**Source:** [https://github.com/apache/superset/issues/35464](https://github.com/apache/superset/issues/35464)
**Type:** Task

## Description
When using Apache Superset 6.0.0rc2, the Swagger UI shows a fetch error:

```
Fetch error
NOT FOUND /api/v1/_openapi
```

This happens after setting the `SUPERSET_APP_ROOT` variable in `superset_config.py` to a custom root path (e.g., `/analytics`).

## Steps to Reproduce
1. Set `SUPERSET_APP_ROOT` in `superset_config.py`, for example:
SUPERSET_APP_ROOT = "/analytics"

2. Restart Superset server.
3. Open Swagger UI, typically at `http://<host>:<port>/swagger/v1`.
4. Observe that the Swagger UI fails to load the OpenAPI specification with the above fetch error.

## Expected Behavior
Swagger UI should load OpenAPI specification from the correct prefixed path, including the `SUPERSET_APP_ROOT` prefix. For example, if `SUPERSET_APP_ROOT = "/analytics"`, Swagger should fetch `/analytics/api/v1/_openapi`.

## Actual Behavior
Swagger UI attempts to fetch the OpenAPI spec from `/api/v1/_openapi` without the prefix, causing a 404 NOT FOUND error.

## Additional Information
- The root path prefix set by `SUPERSET_APP_ROOT` modifies all API endpoints.
- Swagger UI configuration needs adjustment to respect this root path prefix.
- The problem is known to affect custom root path and Swagger integration.
- Restarting Superset and reinitializing with `superset init` does not fix the issue alone.
- Proxy or reverse proxy configurations (e.g., Nginx) may also need matching prefix adjustments.

## Possible Workarounds
- Adjust Swagger UI base path configuration to include the root prefix.
- Use full prefixed URLs when accessing API endpoints directly.
- Check relevant GitHub issues on prefix routing and Swagger UI integration.

### Screenshots/recordings

_No response_

### Superset version

6.0.0rc2

### Python version

3.10

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't fin

... (truncated)

---

### [Task] Helm chart 0.15.1 released but not published

**Source:** [https://github.com/apache/superset/issues/35461](https://github.com/apache/superset/issues/35461)
**Type:** Task

### Bug description

0.15.1 superset chart was released last week, but has not yet been published into https://apache.github.io/superset repository.

Above from that, current 0.15.1 chart is broken, due to infamous Bitnami repositories being deprecated. Not trying to get on politics or suggest what to decide, but a quick workaround could be switching to bitnamilegacy (which most people including myself wont suggest, but is honestly the quickest workaround to fix it).

Any chances to get 6.x at least with a -beta tag or something in charts?

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [ ] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [ ] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Task] [6.0.0rc1] Partial Translations on pt_BR

**Source:** [https://github.com/apache/superset/issues/35330](https://github.com/apache/superset/issues/35330)
**Type:** Task

### Bug description

Title: Partial Portuguese translations in Superset 6.0.0rc1 despite BABEL_DEFAULT_LOCALE configuration

Body:
Describe the bug
After configuring BABEL_DEFAULT_LOCALE = "pt_BR" in superset_config.py and compiling translations manually, some UI elements are still displayed in English while others appear in Portuguese. This occurs on Superset 6.0.0rc1.

To Reproduce
Steps to reproduce the behavior:

1. Use the Docker setup:

```
superset:
    image: apache/superset:6.0.0rc1
    container_name: superset
    restart: always
    build:
      context: .docker/superset
      dockerfile: Dockerfile
    args:
        BUILD_TRANSLATIONS: true
    environment:
      - SUPERSET_LOAD_EXAMPLES=no
      - SUPERSET_CONFIG_PATH=/app/superset_config.py
    ports:
      - "8088:8088"
    depends_on:
      - postgres
    volumes:
      - ./.docker/superset/superset_config.py:/app/superset_config.py
    env_file:
      - ./envs/.superset.env
    command: >
      bash -c "
        superset db upgrade &&
        superset run -h 0.0.0.0 -p 8088
      "
```

2. In `superset_config.py`:
```
BABEL_DEFAULT_LOCALE = "pt_BR"
BABEL_DEFAULT_TIMEZONE = "America/Sao_Paulo"
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "pt_BR": {"flag": "br", "name": "Português (Brasil)"},
}

from superset.translations.utils import get_language_pack

def override_bootstrap_locale(data):
    if data.get("locale") == "pt":
        data["locale"] = "pt_BR"
        data["language_pack"] = get_language_pack('pt_BR')
    return data

COMMON_BOOTSTRAP_OVERRIDES_FUNC = override_bootstrap_locale
```

3. Copy and compile translations:
```
docker exec -it superset bash -c "pybabel compile -d /app/superset/translations"
```

4. Restart Superset and check UI
Expected behavior
All UI elements should be displayed in Portuguese (pt_BR).

Actual behavior
Only some parts of the UI are translated; other strings remain in English. The issue is more noticeable in frontend React elements like dashboard

... (truncated)

---

### [Task] [6.0.0rc2] list of domain names that can embed this dashboard - not showing already added domains

**Source:** [https://github.com/apache/superset/issues/35328](https://github.com/apache/superset/issues/35328)
**Type:** Task

### Bug description

1. On 6.0.0rc2
2. With attached config overrides ( in the comment below )
3. Start with `docker compose -f docker-compose-non-dev.yml up --build -d`
4. Navigate to dashboards
5. Open the `Featured Charts` dashboard
6. Click on three dots -> then embed under some domain like https://mytestdomain.com
7. Save
8. Navigate to datasets
9. Navigate to dashboards again
10. Open the `Featured Charts` dashboard again
11. Click on three dots -> embed
Expected:
- The domains I added will be there
Actual:
- The UI will show an empty input


## Notes
- The input can detect if you enter the same domain again and prevents you from saving, so it's just the UI not reflecting the saved data.
- The console does not show any relevant errors

### Screenshots/recordings

## Loom
.
https://www.loom.com/share/f81fbfccc5474d87b5891c2d195e32a8?sid=ea9d5541-eea4-4659-a370-e7528fa104ac

### Superset version

master / latest-dev

### Python version

Not applicable

### Node version

Not applicable

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [x] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Task] Several errors with docker install and websocket config

**Source:** [https://github.com/apache/superset/issues/35340](https://github.com/apache/superset/issues/35340)
**Type:** Task

### Bug description

Hello !

I still have some trouble with my superset install.
I opened a thread a few weeks ago about issues to configure root application here https://github.com/apache/superset/issues/34773 but I realized that my problems have not connection with that, So I create a new thread for that.

I'm trying to use docker compose to deploy superset in production environment, but I have several issues when the app start.
<img width="1904" height="270" alt="Image" src="https://github.com/user-attachments/assets/c77d71f6-ee94-4987-9f5b-7f71a895ad29" />

<img width="1905" height="254" alt="Image" src="https://github.com/user-attachments/assets/5f118a72-0ed9-4f9d-81a7-859122cacd14" />

<img width="1887" height="450" alt="Image" src="https://github.com/user-attachments/assets/29fa0547-31dd-48f6-a740-998d3e19d20b" />

First, Can you tell me more about websocket, and the intereset to use it ?

My docker/superset_config_docker.py : 
```python
HTML_SANITIZATION = True
HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
  "attributes": {
    "*": ["style", "className", "class"],
  },
  "tagNames": ["style"],
}

GLOBAL_ASYNC_QUERIES = True
GLOBAL_ASYNC_QUERIES_TRANSPORT = "ws"
GLOBAL_ASYNC_QUERIES_WEBSOCKET_URL = "ws://127.0.0.1:8080/"
GLOBAL_ASYNC_QUERIES_JWT_SECRET = "MY_CUSTOM_JWT_KEY"
GLOBAL_ASYNC_QUERIES_JWT_COOKIE_NAME = "async-token"
``` 

```
# Secret key to 
SUPERSET_SECRET_KEY = "MY_CUSTOM_SUPERSET_KEY"

# Set log level
SUPERSET_LOG_LEVEL = debug

# Disable examples
#SUPERSET_LOAD_EXAMPLES = no

# Disable frontend container
BUILD_SUPERSET_FRONTEND_IN_DOCKER = false

# Configuration for websocket connection
JWT_SECRET = "MY_CUSTOM_JWT_KEY"
JWT_COOKIE_NAME = "async-token"
``` 

My nginx configuration : 
```
upstream superset_app {
    server localhost:8088;
    keepalive 100;
}

upstream superset_websocket {
    server localhost:8080;
    keepalive 100;
}

server {
    listen [::]:443 ssl;
    listen 443 ssl;
    server_name my.domain.fr;

    include conf.d/ssl.conf;



... (truncated)

---

### [Task] Boolean fields not rendered correctly for MySQL in Superset 4.1.3

**Source:** [https://github.com/apache/superset/issues/35166](https://github.com/apache/superset/issues/35166)
**Type:** Task

### Bug description

I am using Superset 4.1.3 for MySQL database, and I noticed that boolean fields are not displayed correctly in the Explore/SQL Lab table preview.

For example, fields like:

Enabled

EmailConfirmed

PhoneNumberConfirmed

TwoFactorEnabled

LockoutEnabled

Instead of showing true / false (or 1 / 0), Superset displays them as small icons (stacked lines), making it difficult to read and interpret boolean data.

### Screenshots/recordings

<img width="1168" height="108" alt="Image" src="https://github.com/user-attachments/assets/23847cf1-02d2-4ce4-92aa-4b5c1f4a7f6f" />

### Superset version

4.1.3

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [ ] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [ ] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Task] Bug: Drill to Detail / Drill by Not Working Across Charts from Jinja-Based Datasets

**Source:** [https://github.com/apache/superset/issues/35263](https://github.com/apache/superset/issues/35263)
**Type:** Task

### Bug description

I'm working with three separate datasets, each built using Jinja templating to support dynamic filtering. These datasets are used to power three different charts in a dashboard. All charts share common filter fields (e.g., start_date, Zone, Circle, etc.), and I’ve configured native filters to apply across all charts.

Each dataset uses Jinja to apply filters like this:

**SQL query** is something like this in all 3 datasets.

_WHERE 1=1
{% if filter_values('Zone') %}
  AND "Zone" IN {{ filter_values('Zone') | where_in }}
{% endif %}_


The charts display correct data when filters are applied. However, when I use Drill to Detail or Drill by on any chart, the resulting detail view shows zero records, even though the chart clearly shows data for the selected value.


**Expected Behavior**
Drill to Detail should return the filtered rows from the dataset that match the clicked chart element (e.g., Circle = C1, type_of_node = A).


**Actual Behavior**
Drill to Detail and Drill by return no rows, even though the chart shows non-zero values. This happens consistently across all three charts.


**Notes**
1. All datasets use Jinja templating for dynamic filters.

2. All charts are built from separate datasets, but they share common column names and filter logic.

3. Native filters are scoped correctly to all charts.

4. The issue seems to be with how Superset applies drill filters to Jinja-based queries across multiple datasets.


### Screenshots/recordings

_No response_

### Superset version

4.1.3

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

<img width="1622" height="843" alt="Image" src="https://github.com/user-attachments/assets/c03405bb-d9cb-43db-ab8f-96172019b960" />

### Checklist

- [ ] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors a

... (truncated)

---

### [Task] Timeout errors for embedded Superset dashboard

**Source:** [https://github.com/apache/superset/issues/35261](https://github.com/apache/superset/issues/35261)
**Type:** Task

### Bug description

Current Superset version: 4.0.2

Our platform is set up to embed Superset charts, but we frequently encounter timeout errors in the platform when viewing Superset dashboards.

What we have found is the Superset integration uses a library (@superset-ui/embedded-sdk) to display dashboards. This library creates temporary guest tokens each time a dashboard is viewed — even if the user hasn’t directly logged into Superset. After a timeout (e.g., 15 minutes), the library automatically tries to refresh these tokens. If the user has logged out or their session has ended, these refresh attempts fail, triggering "Insufficient Permissions" errors. The problem worsens if multiple dashboards are viewed, as more tokens are created and retried in parallel.

Can you please get assistance on a proper resolution for this issue?

<img width="679" height="597" alt="Image" src="https://github.com/user-attachments/assets/ee898b43-857e-4d02-90dc-f7eb564e4448" />

### Screenshots/recordings

Attached is an example of the error message displayed upon being logged out while viewing charts

### Superset version

master / latest-dev

### Python version

I don't know

### Node version

I don't know

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [ ] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Task] gevent pulls in a conflicting greenlet

**Source:** [https://github.com/apache/superset/issues/35306](https://github.com/apache/superset/issues/35306)
**Type:** Task

### Bug description

Testing Superset v5.0.0 in a Python 3.10 virtual environment on Linux. In preparation for running via WSGI, I installed `gevent`, but it pulls in an incompatible version of `greenlet`:

```console
$ python -m pip install gevent
Collecting gevent
  Using cached gevent-25.9.1-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (14 kB)
Collecting greenlet>=3.2.2 (from gevent)
  Using cached greenlet-3.2.4-cp310-cp310-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl.metadata (4.1 kB)
Requirement already satisfied: zope.event in ./venv/lib/python3.10/site-packages (from gevent) (6.0)
Requirement already satisfied: zope.interface in ./venv/lib/python3.10/site-packages (from gevent) (8.0.1)
Requirement already satisfied: setuptools>=75.8.2 in ./venv/lib/python3.10/site-packages (from zope.event->gevent) (80.9.0)
Using cached gevent-25.9.1-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (2.2 MB)
Using cached greenlet-3.2.4-cp310-cp310-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl (584 kB)
Installing collected packages: greenlet, gevent
  Attempting uninstall: greenlet
    Found existing installation: greenlet 3.0.3
    Uninstalling greenlet-3.0.3:
      Successfully uninstalled greenlet-3.0.3
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
apache-superset 5.0.0 requires greenlet<=3.1.1,>=3.0.3, but you have greenlet 3.2.4 which is incompatible.
Successfully installed gevent-25.9.1 greenlet-3.2.4
```

The [Superset docs](https://superset.apache.org/docs/configuration/configuring-superset/#running-on-a-wsgi-http-server) recommend using `gevent` with Gunicorn, but don't specify which version. As Superset v5.0.0 requires `greenlet<=3.1.1,>=3.0.3`, it seems the docs should recommend using `gevent==24.2.1`, as that is the last version that satisfies Superset's requirement.

See: https://github.com/gevent/ge

... (truncated)

---

### [Task] Export to excel (row count 50k)

**Source:** [https://github.com/apache/superset/issues/35139](https://github.com/apache/superset/issues/35139)
**Type:** Task

### Bug description

When I download to csv, all rows are loaded. But when I download to excel, 50k rows are loaded. How can I solve this?

### Screenshots/recordings

_No response_

### Superset version

master / latest-dev

### Python version

3.9

### Node version

16

### Browser

Chrome

### Additional context

_No response_

### Checklist

- [ ] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [ ] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---

### [Task] superset helm 0.15.0 chart broken

**Source:** [https://github.com/apache/superset/issues/35174](https://github.com/apache/superset/issues/35174)
**Type:** Task

### Bug description

When using bring your own DB, the superset-init-db k8s main job breaks under this error:

```pgrading DB schema...
Loaded your LOCAL configuration at [/app/pythonpath/superset_config.py]
2025-09-17 12:41:33,296:ERROR:superset.app:Failed to create app
Traceback (most recent call last):
  File "/app/.venv/lib/python3.10/site-packages/superset/app.py", line 40, in create_app
    app_initializer.init_app()
[...]
  File "/app/.venv/lib/python3.10/site-packages/click/core.py", line 1685, in invoke
    super().invoke(ctx)
  File "/app/.venv/lib/python3.10/site-packages/click/core.py", line 1434, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/app/.venv/lib/python3.10/site-packages/click/core.py", line 783, in invoke
    return __callback(*args, **kwargs)
  File "/app/.venv/lib/python3.10/site-packages/click/decorators.py", line 33, in new_func
    return f(get_current_context(), *args, **kwargs)
  File "/app/.venv/lib/python3.10/site-packages/flask/cli.py", line 355, in decorator
    app = __ctx.ensure_object(ScriptInfo).load_app()
  File "/app/.venv/lib/python3.10/site-packages/flask/cli.py", line 309, in load_app
    app = locate_app(import_name, name)
  File "/app/.venv/lib/python3.10/site-packages/flask/cli.py", line 238, in locate_app
    return find_app_by_string(module, app_name)
  File "/app/.venv/lib/python3.10/site-packages/flask/cli.py", line 166, in find_app_by_string
    app = attr(*args, **kwargs)
  File "/app/.venv/lib/python3.10/site-packages/superset/app.py", line 40, in create_app
    app_initializer.init_app()
  File "/app/.venv/lib/python3.10/site-packages/superset/initialization/__init__.py", line 466, in init_app
    self.setup_db()
  File "/app/.venv/lib/python3.10/site-packages/superset/initialization/__init__.py", line 662, in setup_db
    pessimistic_connection_handling(db.engine)
  File "/app/.venv/lib/python3.10/site-packages/flask_sqlalchemy/__init__.py", line 998, in engine
    return self.get_engine(

... (truncated)

---

### [Task] Incompatibility with current versions of "marshmallow" and "flask_limiter"

**Source:** [https://github.com/apache/superset/issues/35169](https://github.com/apache/superset/issues/35169)
**Type:** Task

### Bug description

After installing superset with Python Virtual Environment as described in official guide, superset cannot be launched due to the following errors:

- superset failed to create app. TypeError: Field.__init__() got an unexpected keyword argument 'minLength'
- no module named "flask_limiter.wrapper"

but changing marshmallow version as suggested in [https://github.com/apache/superset/issues/23577](url) and changing flask_limiter version in 3.5.1

the problems are solved

### Screenshots/recordings

_No response_

### Superset version

5.0.0

### Python version

3.11

### Node version

I don't know

### Browser

Not applicable

### Additional context

_No response_

### Checklist

- [x] I have searched Superset docs and Slack and didn't find a solution to my problem.
- [x] I have searched the GitHub issue tracker and didn't find a similar bug report.
- [ ] I have checked Superset's logs for errors and if I found a relevant Python stacktrace, I included it here as text in the "additional context" section.

---
