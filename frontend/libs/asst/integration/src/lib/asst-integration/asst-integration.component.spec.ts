import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstIntegrationComponent } from './asst-integration.component';

describe('AsstIntegrationComponent', () => {
  let component: AsstIntegrationComponent;
  let fixture: ComponentFixture<AsstIntegrationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstIntegrationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstIntegrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
