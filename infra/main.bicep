// Container Apps definition for the Python service.
// Validated in CI with `bicep build`. Never deployed: the live demo runs on Render's free tier.
// Deploying this would require an Azure subscription, which the project deliberately does not use.

targetScope = 'resourceGroup'

@description('Azure region for the demo resources.')
param location string = resourceGroup().location

@description('Container image to deploy, if this ever were deployed.')
param image string = 'ghcr.io/steinantonio/mcp-rag-showcase:latest'

@description('Prefix for resource names.')
param namePrefix string = 'mcprag'

@description('Port the container listens on.')
param targetPort int = 8080

resource logs 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${namePrefix}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource managedEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${namePrefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${namePrefix}-api'
  location: location
  properties: {
    managedEnvironmentId: managedEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: image
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'MCP_RAG_CORPUS'
              value: '/app/corpus'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 2
      }
    }
  }
}

output url string = 'https://${app.properties.latestRevisionFqdn}'
