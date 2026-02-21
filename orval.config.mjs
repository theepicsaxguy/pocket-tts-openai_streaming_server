import { defineConfig } from 'orval';

export default defineConfig({
  studio: {
    input: {
      target: './openapi.yaml',
    },
    output: {
      target: './static/js/studio/client.ts',
      client: 'axios',
      override: {
        mutator: {
          path: './static/js/studio/custom-instance.ts',
          name: 'customInstance',
        },
      },
    },
  },
});
