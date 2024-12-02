### Build Command

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

---

### Run Command

To start the server, execute:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

### Environment Variables

- `NEON_PROJECT_ID`: Neon project ID available from Neon Console
- `NEON_HOST`: Neon host available from Neon Console
- `NEON_API_KEY`: Neon API key available from Neon Console
- `NEON_BRANCH_ID`: Neon branch ID available from Neon Console. Typically for your main branch. From Neon Console > Branches > Main > Branch ID

